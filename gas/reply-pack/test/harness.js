// Google Apps Script の部品を差し替えて Code.gs を node で動かすための道具（テスト専用）
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const CODE = fs.readFileSync(path.join(__dirname, '..', 'Code.gs'), 'utf8');

function a1(rows, r, c, nr, nc) {
  const out = [];
  for (let i = 0; i < nr; i++) {
    const row = [];
    for (let j = 0; j < nc; j++) {
      const line = rows[r - 1 + i] || [];
      const v = line[c - 1 + j];
      row.push(v === undefined ? '' : v);
    }
    out.push(row);
  }
  return out;
}

class MockSheet {
  constructor(name, id, formUrl) { this.name = name; this.id = id; this.rows = []; this.formUrl = formUrl || null; }
  getName() { return this.name; }
  getSheetId() { return this.id; }
  getFormUrl() { return this.formUrl; }
  getLastRow() {
    for (let i = this.rows.length - 1; i >= 0; i--) {
      if ((this.rows[i] || []).some((v) => v !== '' && v !== undefined && v !== null)) return i + 1;
    }
    return 0;
  }
  getLastColumn() { return this.rows.reduce((m, r) => Math.max(m, (r || []).length), 0); }
  setFrozenRows() {}
  appendRow(vals) { this.rows[this.getLastRow()] = vals.slice(); }
  getRange(r, c, nr, nc) {
    nr = nr || 1; nc = nc || 1;
    const sheet = this;
    return {
      getValues: () => a1(sheet.rows, r, c, nr, nc),
      setValues: (vals) => {
        if (vals.length !== nr || vals[0].length !== nc) throw new Error('setValues size mismatch');
        for (let i = 0; i < nr; i++) {
          sheet.rows[r - 1 + i] = sheet.rows[r - 1 + i] || [];
          for (let j = 0; j < nc; j++) sheet.rows[r - 1 + i][c - 1 + j] = vals[i][j];
        }
      },
      setValue: (v) => {
        sheet.rows[r - 1] = sheet.rows[r - 1] || [];
        sheet.rows[r - 1][c - 1] = v;
      }
    };
  }
}

function formatDate(d, tz, pattern) {
  const parts = {};
  new Intl.DateTimeFormat('en-US', {
    timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
  }).formatToParts(d).forEach((p) => { parts[p.type] = p.value; });
  return pattern
    .replace('yyyy', parts.year).replace('MM', parts.month).replace('dd', parts.day)
    .replace('HH', parts.hour).replace('mm', parts.minute).replace('ss', parts.second)
    .replace(/\bH\b/, String(Number(parts.hour)));
}

function createEnv(opts) {
  opts = opts || {};
  const sheets = [];
  let nextId = 100;
  const ss = {
    getSheetByName: (n) => sheets.find((s) => s.name === n) || null,
    insertSheet: (n) => { const s = new MockSheet(n, nextId++); sheets.push(s); return s; },
    getSheets: () => sheets.slice(),
    getUrl: () => 'https://docs.google.com/spreadsheets/d/TEST/edit',
    addFormSheet: (name, headers) => {
      const s = new MockSheet(name, nextId++, 'https://docs.google.com/forms/d/FORM/edit');
      s.rows.push(headers.slice());
      sheets.push(s);
      return s;
    }
  };
  const alerts = [];
  const mails = [];
  const fetches = [];
  const drafts = [];
  const props = {};
  const cache = {};
  const triggers = [];
  let mailQuota = opts.mailQuota === undefined ? 100 : opts.mailQuota;
  let fetchHandler = opts.fetchHandler || (() => ({ code: 200, body: '{}' }));
  let lockAvailable = true;
  let uuid = 0;

  const ctx = {
    console,
    SpreadsheetApp: {
      getActive: () => ss,
      getUi: () => ({
        alert: (m) => alerts.push(m),
        createMenu: () => { const b = { addItem: () => b, addSeparator: () => b, addToUi: () => b }; return b; }
      })
    },
    MailApp: {
      sendEmail: (o) => {
        if (opts.mailThrows) throw new Error(opts.mailThrows);
        if (mailQuota <= 0) throw new Error('Service invoked too many times for one day: email.');
        mailQuota--; mails.push(o);
      },
      getRemainingDailyQuota: () => mailQuota
    },
    UrlFetchApp: {
      fetch: (url, o) => {
        fetches.push({ url, opts: o, payload: o.payload ? JSON.parse(o.payload) : null });
        const r = fetchHandler(url, o, fetches.length);
        return { getResponseCode: () => r.code, getContentText: () => r.body || '' };
      }
    },
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
        setProperty: (k, v) => { props[k] = String(v); },
        deleteProperty: (k) => { delete props[k]; },
        getProperties: () => Object.assign({}, props)
      })
    },
    CacheService: {
      getScriptCache: () => ({ get: (k) => cache[k] || null, put: (k, v) => { cache[k] = v; } })
    },
    LockService: {
      getScriptLock: () => ({ tryLock: () => lockAvailable, waitLock: () => {}, releaseLock: () => {} })
    },
    Utilities: {
      formatDate,
      getUuid: () => 'uuid-' + (++uuid),
      computeDigest: (alg, s) => Array.from(crypto.createHash('sha256').update(String(s), 'utf8').digest()).map((b) => (b > 127 ? b - 256 : b)),
      DigestAlgorithm: { SHA_256: 'SHA_256' },
      Charset: { UTF_8: 'UTF_8' },
      sleep: () => {}
    },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'shop@example.com' }) },
    ScriptApp: {
      AuthMode: { FULL: 'FULL' },
      WeekDay: { MONDAY: 'MONDAY' },
      requireAllScopes: () => {},
      getProjectTriggers: () => triggers.slice(),
      deleteTrigger: (t) => { const i = triggers.indexOf(t); if (i >= 0) triggers.splice(i, 1); },
      newTrigger: (fn) => {
        const t = { fn, kind: [], getHandlerFunction: () => fn };
        const b = {
          forSpreadsheet: () => { t.kind.push('spreadsheet'); return b; },
          onFormSubmit: () => { t.kind.push('formSubmit'); return b; },
          timeBased: () => { t.kind.push('time'); return b; },
          everyMinutes: (n) => { t.kind.push('every' + n); return b; },
          onWeekDay: (d) => { t.kind.push(d); return b; },
          atHour: (h) => { t.kind.push('at' + h); return b; },
          create: () => { triggers.push(t); return t; }
        };
        return b;
      }
    },
    GmailApp: {
      threads: [],
      labels: {},
      lastQuery: null,
      getUserLabelByName: (n) => ctx.GmailApp.labels[n] || null,
      createLabel: (n) => { ctx.GmailApp.labels[n] = { name: n }; return ctx.GmailApp.labels[n]; },
      search: (q) => { ctx.GmailApp.lastQuery = q; return ctx.GmailApp.threads.filter((t) => !t.labeled); },
      createDraft: (to, subject, body) => { drafts.push({ to, subject, body }); return {}; }
    }
  };
  vm.createContext(ctx);
  vm.runInContext(CODE, ctx, { filename: 'Code.gs' });

  let clock = opts.now || new Date('2026-11-24T01:00:00Z'); // 日本時間 10:00
  ctx.now_ = () => new Date(clock.getTime());

  return {
    ctx, ss, sheets, alerts, mails, fetches, drafts, props, cache, triggers,
    setNow: (d) => { clock = d; },
    setFetch: (fn) => { fetchHandler = fn; },
    setLock: (v) => { lockAvailable = v; },
    setMailQuota: (n) => { mailQuota = n; },
    sheet: (n) => ss.getSheetByName(n),
    /** 設定シートを作り、項目に値を入れる */
    configure: (values) => {
      ctx.ensureSheets_();
      const st = ss.getSheetByName('設定');
      for (let i = 1; i < st.rows.length; i++) {
        const k = st.rows[i][0];
        if (k in values) st.rows[i][1] = values[k];
      }
    },
    logRows: () => ss.getSheetByName('受付記録').rows.slice(1)
  };
}

const BASE_SETTINGS = {
  '店名': 'テスト工務店',
  'お客さま連絡先メール': 'owner@example.com',
  '見守り先メール': 'watch@example.com',
  '署名': 'テスト工務店 099-000-0000',
  'LINEチャネルアクセストークン': 'TOKEN-SECRET-123',
  'LINE通知先ユーザーID': 'U' + 'a'.repeat(32)
};

const FORM_HEADERS = ['タイムスタンプ', 'お名前', 'メールアドレス', '電話番号', 'お問い合わせ内容', 'ご希望の時期'];

module.exports = { createEnv, BASE_SETTINGS, FORM_HEADERS };
