$(document).ready(function (){

    let textarea = document.querySelector('textarea');

    textarea.addEventListener('keydown', autosize);
    textarea.style.cssText = 'height:auto; padding:0';
    textarea.style.cssText = 'height:' + (textarea.scrollHeight + 10) + 'px';

    function autosize(){
      let el = this;
      setTimeout(function(){
        el.style.cssText = 'height:auto; padding:0';
        // for box-sizing other than "content-box" use:
        // el.style.cssText = '-moz-box-sizing:content-box';
        el.style.cssText = 'height:' + el.scrollHeight + 'px';
      },0);
    }

})