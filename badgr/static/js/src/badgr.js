/* Javascript for BadgrXBlock. */
function BadgrXBlock(runtime, element, data) {
  console.log(
    "INFO In BadgrXBlock.. the runtime is: " + JSON.stringify(runtime.keys)
  );
  console.log("INFO IN BadgrXBlock.. the data is: " + JSON.stringify(data));
  var user = data.user;
  var my_url =
    "https://learn.firstcontactcrypto.com/api/grades/v1/subsection/" +
    data.course_id +
    "/?user_id=" +
    user.id;
  var section_title = data.section_title;
  var pass_mark = data.pass_mark;
  var award_message = data.award_message;
  var badge_slug = data.badge_slug;
  var motivation_message = data.motivation_message;
  var handlerUrl = runtime.handlerUrl(element, "new_award_badge");
  var noAwardUrl = runtime.handlerUrl(element, "no_award_received");
  // var passedTestUrl = runtime.handlerUrl(element, "passed_test")
  // var testXblockTreeUrl = runtime.handlerUrl(element, "test_xblock_tree")
  var onlyUrl = location.href.replace(location.search, "");
  var conditionStatusHandlerURL = runtime.handlerUrl(
    element,
    "condition_status_handler"
  );

  // function scrollPage(target) {
  //     if (target.length) {
  //     // Only prevent default if animation is actually gonna happen
  //     event.preventDefault();
  //     $("html, body").animate(
  //         {
  //         scrollTop: target.offset().top
  //         },
  //         1000,
  //         function() {
  //         // Callback after animation
  //         // Must change focus!
  //         var $target = $(target);
  //         $target.focus();
  //         if ($target.is(":focus")) {
  //             // Checking if the target was focused
  //             return false;
  //         } else {
  //             $target.attr("tabindex", "-1"); // Adding tabindex for elements not focusable
  //             $target.focus(); // Set focus again
  //         }
  //         }
  //     );
  //     }
  // }

  const sleep = milliseconds => {
    console.log("INFO In SLEEP.. sleeping for " + milliseconds + " millis");
    return new Promise(resolve => setTimeout(resolve, milliseconds));
  };

  function getGrades(data) {
    // * original_grade: An object representation of a users original grade containing:
    //     * earned_all: The float score a user earned for all graded and not graded problems
    //     * possible_all: The float highest score a user can earn for all graded and not graded problems
    //     * earned_graded: The float score a user earned for only graded probles
    //     * possible_graded: The float highest score a user can earn for only graded problems

    console.log("INFO In getGrades.. the data is: " + JSON.stringify(data));

    var passed_test = null;
    var error_state = false;
    // var incomplete_state = false;
    var abort = null;
    var mdata = null

    $.ajax({
      type: "POST",
      url: conditionStatusHandlerURL,
      data: JSON.stringify({ blah: "blah" }),
      // async: false,
      success: function(result, status, xhr) {
        console.log(
          "SUCCESS In getGrades.. (conditionStatusHandlerURL) status: " + status + "result is: " + JSON.stringify(result));
        mdata = result
        if (result.abort === "True") {
          abort = true; // the user did not answer the question, so don't let 'em in... good bye sucker, the button stays disabled and nothing happens
        } else {
          $("#lean_overlay").show();
          $(".badge-loader").show();
          // incomplete_state = true 
          abort = false;
        }
        if (result.status === "True") {
          passed_test = true
        }
        else {
          passed_test = false;
        }

        console.log("INFO In getGrades.. abort = " + JSON.stringify(abort))
        
        if (abort === false && passed_test === true && error_state === false && mdata.check_earned === 'False') {
          $.ajax({
            type: "POST",
            url: handlerUrl,
            // async: false,
            data: JSON.stringify({ name: "badgr" }),
            success: function(json) {
              // Just reload the page, the correct html with the badge will be displayed
              var onlyUrl = location.href.replace(
                location.search,
                "#" + self.section_title
              );
              window.location = onlyUrl;
              console.log("SUCCESS In getGrades.. (handlerUrl)");
              // return false;
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
              location.href.replace(location.search, "#" + self.section_title);
              console.log(
                "ERROR In getGrades.. (handlerUrl)" +
                  xhr.status +
                  ": " +
                  xhr.responseText
              );
              error_state = true;
            }
          });
        } else {
          if (error_state === false && abort === false && mdata.check_earned === 'False') {
            $.ajax({
              type: "POST",
              url: noAwardUrl,
              // async: false,
              data: JSON.stringify({ name: "badgr" }),
              success: function(json) {
                $(".badge-loader").hide();
                $("#lean_overlay").hide();
                var $motivation = $(
                  '<p class="badgr-motivation">' + motivation_message + "</p>"
                );
                $(".badgr_block").append($motivation);
                $("#check-for-badge").remove();
                location.href.replace(location.search, "#lean_overlay");
                console.log("SUCCESS In getGrades.. (noAwardUrl)");
              },
              error: function(xhr, msg, error) {
                console.log(
                  "ERROR In getGrades.. (noAwardUrl)" +
                    xhr.status +
                    ": " +
                    xhr.responseText
                );
              }
            });
          } 
        }
      },
      error: function(xhr, status, error) {
        console.log(
          "ERROR In getGrades.. (conditionStatusHandlerURL)" +
            xhr.status +
            ": " +
            xhr.responseText
        );
        error_state = true
        abort = false;
      }
    });

    // console.log("INFO In getGrades.. abort = " + JSON.stringify(abort))

    // while (abort === null) {
    //   sleep(500)
    // }

    // if (abort === false && passed_test === true && error_state === false && mdata.check_earned === 'False') {
    //   $.ajax({
    //     type: "POST",
    //     url: handlerUrl,
    //     // async: false,
    //     data: JSON.stringify({ name: "badgr" }),
    //     success: function(json) {
    //       // Just reload the page, the correct html with the badge will be displayed
    //       var onlyUrl = location.href.replace(
    //         location.search,
    //         "#" + self.section_title
    //       );
    //       window.location = onlyUrl;
    //       console.log("SUCCESS In getGrades.. (handlerUrl)");
    //       // return false;
    //     },
    //     error: function(xhr, errmsg, err) {
    //       $(".badge-loader").hide();
    //       $("#lean_overlay").hide();
    //       $("#check-for-badge").remove();
    //       $("#results").html(
    //         "<div>Oops! We have encountered an error, the badge " +
    //           '"' +
    //           badge_slug +
    //           '"' +
    //           " does not exist. Please contact your support administrator." +
    //           "</div>"
    //       ); // add the error to the dom
    //       location.href.replace(location.search, "#" + self.section_title);
    //       console.log(
    //         "ERROR In getGrades.. (handlerUrl)" +
    //           xhr.status +
    //           ": " +
    //           xhr.responseText
    //       );
    //       error_state = true;
    //     }
    //   });
    // } else {
    //   if (error_state === false && abort === false && mdata.check_earned === 'False') {
    //     $.ajax({
    //       type: "POST",
    //       url: noAwardUrl,
    //       // async: false,
    //       data: JSON.stringify({ name: "badgr" }),
    //       success: function(json) {
    //         $(".badge-loader").hide();
    //         $("#lean_overlay").hide();
    //         var $motivation = $(
    //           '<p class="badgr-motivation">' + motivation_message + "</p>"
    //         );
    //         $(".badgr_block").append($motivation);
    //         $("#check-for-badge").remove();
    //         location.href.replace(location.search, "#lean_overlay");
    //         console.log("SUCCESS In getGrades.. (noAwardUrl)");
    //       },
    //       error: function(xhr, msg, error) {
    //         console.log(
    //           "ERROR In getGrades.. (noAwardUrl)" +
    //             xhr.status +
    //             ": " +
    //             xhr.responseText
    //         );
    //       }
    //     });
    //   } else if (error_state === false && abort === true) {
    //     console.log("INFO In getGrades.. error_state === false && abort === true")
    //     // location.reload(true);
    //   }
    // }
  }
  $("#check-for-badge").click(function(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    getGrades(data);
    // $.ajax({
    //     type: "GET",
    //     url: my_url,
    //     success: function(data, status, xhr) {
    //         getGrades(data)
    //         console.log("SUCCESS In getGrades.. (my_url)" + xhr.status + ": " + xhr.responseText);
    //     },
    //     error: function(xhr, errmsg, err) {
    //       console.log("SUCCESS In getGrades.. (my_url)" + xhr.status + ": " + xhr.responseText);
    //     }
    // });
  });
}

// EDITED BY MY
// https://css-tricks.com/snippets/jquery/smooth-scrolling/
// Select all links with hashes
// $('a[href*="#"]')
//   // Remove links that don't actually link to anything
//   .not('[href="#"]')
//   .not('[href="#0"]')
//   .click(function(event) {
//     // On-page links
//     if (
//       location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '')
//       &&
//       location.hostname == this.hostname
//     ) {
//       // Figure out element to scroll to
//       var target = $(this.hash);
//       target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
//       // Does a scroll target exist?
//       if (target.length) {
//         // Only prevent default if animation is actually gonna happen
//         event.preventDefault();
//         $('html, body').animate({
//           scrollTop: target.offset().top
//         }, 1000, function() {
//           // Callback after animation
//           // Must change focus!
//           var $target = $(target);
//           $target.focus();
//           if ($target.is(":focus")) { // Checking if the target was focused
//             return false;
//           } else {
//             $target.attr('tabindex','-1'); // Adding tabindex for elements not focusable
//             $target.focus(); // Set focus again
//           };
//         });
//       }
//     }
//   });
