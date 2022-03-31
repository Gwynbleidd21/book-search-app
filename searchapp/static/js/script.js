$(".owl-carousel").owlCarousel({
    autoplay: true,
    autoplayHoverPauseuse: true,
    autoplayTimeoutt: 100,
    items: 3,
    nav: true,
    loop: true,
    margin: 5,
    padding: 5,
    stagePadding: 5
    }
);

let input = document.querySelector("#title")
let button = document.querySelector("#author")

button.disabled = true

input.addEventListener("change", stateHandle)

function stateHandle() {
  if (document.querySelector("title").value === "") {
    button.disabled = true
      button.innerHTML = '';
  } else {
    button.disabled = false
  }
}