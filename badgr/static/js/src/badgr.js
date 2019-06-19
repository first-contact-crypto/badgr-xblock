/* Javascript for BadgrXBlock. */
function BadgrXBlock(runtime, element, data) {
  var user = data.user;
  // var my_url =
  //   "/api/grades/v1/course_grade/" +
  //   data.course_id +
  //   "/users/?username=" +
  //   user;
  var my_url = "https://learn.firstcontactcrypto.com/courses/" + data.course_id + "?" + "username=" + user
  var section_title = data.section_title;
  var pass_mark = data.pass_mark;
  var award_message = data.award_message;
  var badge_slug = data.badge_slug;
  var motivation_message = data.motivation_message;
  var handlerUrl = runtime.handlerUrl(element, "new_award_badge");
  var noAwardUrl = runtime.handlerUrl(element, "no_award_received");
  var onlyUrl = location.href.replace(location.search, "");

  function getGrades(data) {
    console.log("INFO In getGrades..")
    alert("INFO: In getGrades.. data is " + JSON.stringify(data.json())

    if (data.success === "correct") {
      $.ajax({
        type: "POST",
        url: handlerUrl,
        data: JSON.stringify({ name: "badgr" }),
        success: function(json) {
          // Just reload the page, the correct html with the badge will be displayed
          var onlyUrl = location.href.replace(location.search, "");
          window.location = onlyUrl;
          return true;
        },
        error: function(xhr, errmsg, err) {
          $(".badge-loader").hide();
          $("#lean_overlay").hide();
          $("#check-for-badge").remove();
          $("#results").html(
            "<div>Oops! We have encountered an error, the badge " +
              '"' +
              badge_slug +
              '"' +
              " does not exist. Please contact your support administrator." +
              "</div>"
          ); // add the error to the dom
          console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
          return false
        }
      });
    } else {
      $.ajax({
        type: "POST",
        url: noAwardUrl,
        data: JSON.stringify({ name: "badgr" }),
        success: function(json) {
          $(".badge-loader").hide();
          $("#lean_overlay").hide();
          var $motivation = $(
            '<p class="badgr-motivation">' + motivation_message + "</p>"
          );
          $(".badgr_block").append($motivation);
          $("#check-for-badge").remove();
        }
      });
    }




  $("#check-for-badge").click(function(event) {
    alert("INFO in check-for-badge().click().. calling getGrades(data)")

    event.preventDefault();
    event.stopImmediatePropagation();
    $("#lean_overlay").show();
    $(".badge-loader").show();
    $.ajax({
      type: "GET",
      url: my_url,
      success: function (data) {
        alert("INFO in check-for-badge().click().. calling getGrades(data)")
        getGrades(data)
    });
  });
}



// EDITED BY MY 
// https://css-tricks.com/snippets/jquery/smooth-scrolling/
// Select all links with hashes
$('a[href*="#"]')
  // Remove links that don't actually link to anything
  .not('[href="#"]')
  .not('[href="#0"]')
  .click(function(event) {
    // On-page links
    if (
      location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') 
      && 
      location.hostname == this.hostname
    ) {
      // Figure out element to scroll to
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      // Does a scroll target exist?
      if (target.length) {
        // Only prevent default if animation is actually gonna happen
        event.preventDefault();
        $('html, body').animate({
          scrollTop: target.offset().top
        }, 1000, function() {
          // Callback after animation
          // Must change focus!
          var $target = $(target);
          $target.focus();
          if ($target.is(":focus")) { // Checking if the target was focused
            return false;
          } else {
            $target.attr('tabindex','-1'); // Adding tabindex for elements not focusable
            $target.focus(); // Set focus again
          };
        });
      }
    }
});