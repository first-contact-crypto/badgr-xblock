/* Javascript for BadgrXBlock. */
function BadgrXBlock(runtime, element, data) {
  console.log("INFO In BadgrXBlock.. the runtime is: " + JSON.stringify(runtime.keys))
  console.log("INFO IN BadgrXBlock.. the data is: " + JSON.stringify(data))
    var user = data.user;
    var my_url =
        "/api/grades/v1/course_grade/" +
        data.course_id +
        "/users/?username=" +
        user;
    var my_url = "https://learn.firstcontactcrypto.com/api/grades/v1/subsection/" + data.course_id + "/?user_id=" + user 
    var section_title = data.section_title;
    var pass_mark = data.pass_mark;
    var award_message = data.award_message;
    var badge_slug = data.badge_slug;
    var motivation_message = data.motivation_message;
    var handlerUrl = runtime.handlerUrl(element, "new_award_badge");
    var noAwardUrl = runtime.handlerUrl(element, "no_award_received");
    var passedTestUrl = runtime.handlerUrl(element, "passed_test")
    var testXblockTreeUrl = runtime.handlerUrl(element, "test_xblock_tree")
    var onlyUrl = location.href.replace(location.search, "");

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

    function getGrades(data) {
        // * original_grade: An object representation of a users original grade containing:
        //     * earned_all: The float score a user earned for all graded and not graded problems
        //     * possible_all: The float highest score a user can earn for all graded and not graded problems
        //     * earned_graded: The float score a user earned for only graded probles
        //     * possible_graded: The float highest score a user can earn for only graded problems

        console.log("INFO In getGrades.. the data is: " + JSON.stringify(data))

        $.ajax({
          type: "POST",
          url: testXblockTreeUrl,
          data: {"blah":"blah"},
          error: function(xhr, status, error) {
            console.log("ERROR In getGrades.. " + status + error)
          }
        })

        // var passed_test = None 

        // $.ajax({
        //   type: "POST",
        //   url: passedTestUrl,
        //   success: function(data, status, xhr) {
        //     if (typeof(data) === typeof("")) {
        //       console.log("ERROR in getGrades: " + data)
        //     }
        //     else if (typeof(data) === typeof(true)) {
        //       console.log("SUCCESS In getGrades.. passed_test = " + data.toString)
        //       passed_test = data
        //     }
        //     else {
        //       console.log("ERROR In getGrades: I don't know what type the returned handler data is!")
        //     }
        //   },
        //   error: function(xhr, status, error) {
        //     console.log("ERROR: In getGrades.. " + status + " " + error)
        //   }
        // })

        // if (passed_test) {
        //     $.ajax({
        //         type: "POST",
        //         url: handlerUrl,
        //         data: JSON.stringify({ name: "badgr" }),
        //         success: function (json) {
        //             // Just reload the page, the correct html with the badge will be displayed
        //             var onlyUrl = location.href.replace(location.search, "");
        //             window.location = onlyUrl;
        //             return false;
        //         },
        //         error: function (xhr, errmsg, err) {
        //             $(".badge-loader").hide();
        //             $("#lean_overlay").hide();
        //             $("#check-for-badge").remove();
        //             $("#results").html(
        //                 "<div>Oops! We have encountered an error, the badge " +
        //                 '"' +
        //                 badge_slug +
        //                 '"' +
        //                 " does not exist. Please contact your support administrator." +
        //                 "</div>"
        //             ); // add the error to the dom
        //             console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        //         }
        //     });
        // } else {
        //     $.ajax({
        //         type: "POST",
        //         url: noAwardUrl,
        //         data: JSON.stringify({ name: "badgr" }),
        //         success: function (json) {
        //             $(".badge-loader").hide();
        //             $("#lean_overlay").hide();
        //             var $motivation = $(
        //                 '<p class="badgr-motivation">' + motivation_message + "</p>"
        //             );
        //             $(".badgr_block").append($motivation);
        //             $("#check-for-badge").remove();
        //         }
        //     });
        // }
    }

    $("#check-for-badge").click(function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        $("#lean_overlay").show();
        $(".badge-loader").show();
        // $.ajax({
        //     type: "GET",
        //     url: my_url,
        //     success: getGrades(data),
        //     error: function (xhr, errmsg, err) {
        //       console.log("ERROR In (#check-for-badge).click.. API call failed" + err + " " + errmsg)
        //     }
        // });
        
        // ########### ERASE ME
        getGrades(data)
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