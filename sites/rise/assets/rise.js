(function(){
  var d=document,root=d.documentElement;
  /* メニュー（スマホ） */
  var btn=d.querySelector('.menu-btn');
  if(btn){
    btn.addEventListener('click',function(){
      var open=root.classList.toggle('menu-open');
      btn.setAttribute('aria-expanded',open?'true':'false');
    });
    d.querySelectorAll('.gnav a').forEach(function(a){a.addEventListener('click',function(){root.classList.remove('menu-open');btn.setAttribute('aria-expanded','false')})});
  }
  /* ふわっと表示 */
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els=d.querySelectorAll('.sh,.pcard,.wbox,.rcard,.pc,.duo,.msg,.cpc,.steps li,.faqlist details,.shop,.igc,.yc,.oc,.fwgrid li,.fc,.intro .txt,.intro .ph,.result .big,.result figure,.ac,.pbox,.answer,.concept .txt,.mini4');
  if(!reduce&&'IntersectionObserver' in window){
    els.forEach(function(e,i){e.classList.add('rv');e.style.transitionDelay=((i%4)*80)+'ms'});
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}})},{threshold:.12,rootMargin:'0px 0px -40px 0px'});
    els.forEach(function(e){io.observe(e)});
  }
})();
