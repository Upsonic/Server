function typeWriter(id_name, text, i, speed, pass=false) {
    the_element = document.getElementById(id_name);
    the_text = text;


    if (the_element.textContent == "$ " || pass == true) {
        if (i < the_text.length) {
            the_element.innerHTML += the_text.charAt(i);
            i++;
            setTimeout(typeWriter, speed, id_name, text, i, speed, true);
        }
    }
}




const left_light = document.querySelector(".sticky_light_right_img");
const right_light = document.querySelector(".sticky_light_left_img");



const blue_sticky = document.querySelector(".blue_sticky");
const purple_sticky = document.querySelector(".purple_sticky");
const red_sticky = document.querySelector(".red_sticky");

const green_sticky = document.querySelector(".green_sticky");
const white_sticky = document.querySelector(".white_sticky");


// create a const that low by 20% of top



const blue_sticky_observer = new IntersectionObserver( 
  ([e]) => e.target.classList.toggle("blue_sticky_pinned", e.intersectionRatio < 1),
  { threshold: [1] }
);
blue_sticky_observer.observe(blue_sticky);




const purple_sticky_observer = new IntersectionObserver( 
    ([e]) => e.target.classList.toggle("purple_sticky_pinned", e.intersectionRatio < 1),
    { threshold: [1] }
  );
  purple_sticky_observer.observe(purple_sticky);



  const red_sticky_observer = new IntersectionObserver( 
    ([e]) => e.target.classList.toggle("red_sticky_pinned", e.intersectionRatio < 1),
    { threshold: [1] }
  );
  red_sticky_observer.observe(red_sticky);




    const green_sticky_observer = new IntersectionObserver(
        ([e]) => e.target.classList.toggle("green_sticky_pinned", e.intersectionRatio < 1),
        { threshold: [1] }
    );
    green_sticky_observer.observe(green_sticky);


    const white_sticky_observer = new IntersectionObserver(
        ([e]) => e.target.classList.toggle("white_sticky_pinned", e.intersectionRatio < 0.2),
        { threshold: [1] }
    );
    white_sticky_observer.observe(white_sticky);





  window.addEventListener("scroll", () => {

    const blue_active = document.querySelector(".blue_sticky_pinned");
    const purple_active = document.querySelector(".purple_sticky_pinned");
    const red_active = document.querySelector(".red_sticky_pinned");

    const green_active = document.querySelector(".green_sticky_pinned");
    const white_active = document.querySelector(".white_sticky_pinned");





    // if just blue is active 
    if (!blue_active) {
        left_light.style.display = "block";
        left_light.src = "/static/images/right_light_1.svg";
        typeWriter("deploying_type_write", "Deployed in 1 second", 0, 50);

    }
    if (!purple_active) {
        left_light.style.display = "block";
        left_light.src = "/static/images/right_light_1_purple.svg";
        typeWriter("deploying_without_restart_type_write", "All systems online, Uptime %100", 0, 50);

    }

    if (!red_active) {
        left_light.style.display = "block";
        left_light.src = "/static/images/right_light_1_red.svg";
        typeWriter("2x_faster_restart_type_write", "Just continue to other issue.", 0, 50);
        

    }



    if (!green_active) {
        left_light.style.display = "block";
        left_light.src = "/static/images/right_light_1_green.svg";
        typeWriter("durability_restart_type_write", "An exception thrown, snoozed the statement and waiting for fix.", 0, 50);

    }

    if (!white_active) {
        left_light.style.display = "none";

    }




});





