(() => {
  'use strict';
  document.querySelectorAll('[data-simulation]').forEach(panel=>{
    if(panel.dataset.enhanced)return;
    panel.dataset.enhanced='true';
    const range=panel.querySelector('[data-sim-step]'),select=panel.querySelector('[data-sim-scenario]');
    let steps;
    function draw(){
      const index=Number(range.value),step=steps[index];
      panel.querySelector('[data-sim-label]').textContent=`Step ${index+1}/${steps.length}: ${step.label}`;
      panel.querySelector('[data-sim-detail]').textContent=step.detail;
      panel.querySelector('[data-sim-svg]').textContent=step.label;
      panel.querySelector('[data-sim-state]').textContent=JSON.stringify(step.state,null,2);
      panel.querySelector('[data-sim-prev]').disabled=index===0;
      panel.querySelector('[data-sim-next]').disabled=index===steps.length-1;
    }
    function reset(){steps=window.GuideSimulations.simulate(panel.dataset.simulation,select.value==='failure').steps;range.max=steps.length-1;range.value=0;draw();}
    range.addEventListener('input',draw);select.addEventListener('change',reset);
    panel.querySelector('[data-sim-prev]').addEventListener('click',()=>{range.stepDown();draw();});
    panel.querySelector('[data-sim-next]').addEventListener('click',()=>{range.stepUp();draw();});
    panel.querySelector('[data-sim-reset]').addEventListener('click',reset);reset();
  });
})();
