/* Javascript for EncryptedXBlock. */

/*
        The logic of render the first page has been move to the "docreaderxblockBaidu.html" page, since there are multiple
    logic here, and put the logic in this page below will greatly increase the difficulty to response to all the require-
    ment and logic flow here. 

        For this page, the only variable that we care is the $('iframe', element)[0].src. That means, what we need to do is
    to retrieve the value from the backend. Since the address of src is a dynamic address, it means:

            1. for the creation of the xblock, we need to do a onload loading in order for the page to get the dynamic address,
        In this case, we need to change the src address after the ajax request.
            2. for the modifying of the address, we need to:
        
        if the customer just change the name of the block, then we need to store the src in a field, since when we save
        the new name, the lms page won't load any ajax, in this case, the $('iframe', element)[0].src will again become a empty
    string that result in a blank page, in this case, when the client change the name or upload a new page, what we need to do is 
    to set a variable 
*/

/*
    (
        function()
        {
            console.log("automatically function");
            var handler_url = runtime.handlerUrl(element, "initiate_address");
            var baidu_view_proxy_url = runtime.handlerUrl(element, "baidu_view_proxy");

            var dict = {
                "hello": "world",
                "baidu_view_proxy_url":baidu_view_proxy_url,
            }

            $.ajax
            (
                {
                    type: "POST",
                    url: handler_url,
                    data: JSON.stringify(dict),
                    success: function(responseData)
                    {
                        $('iframe', element)[0].src = responseData.baidu_view_proxy_url;
                        console.log("right situation");

                    },
                    error: function(responseData)
                    {
                        console.log("wrong situation");
                    }
                }
            );
        }
    )();
*/

function DocReaderXBlock(runtime, element) 
{
    
    function parse_cookie_and_get_value(key_name_para)
    {
        var cookie_value = null;
        if (document.cookie && document.cookie != '')
        {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++)
            {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, key_name_para.length + 1) == (key_name_para + '=')) 
                {
                    cookie_value = decodeURIComponent(cookie.substring(key_name_para.length + 1));
                    break;
                }
            }
        }
        return cookie_value;
    }

    // due to baidu.doc.js's bug, the following cannot be executed since it follows a baidu error.
    // function loop_height()
    // {
    //     var loop_int = null;

    //     function check()
    //     {

    //         console.log("enter check");
    //         console.log($('iframe', element));


    //         if (       $('iframe', element)[0]   )
    //         {
    //             if ($('iframe', element)[0].contentWindow.document.body.getElementsByTagName("iframe")[0])
    //             {
    //                 clearInterval(loop_int);
    //                 $('iframe', element)[0].style.height = $('iframe', element)[0].contentWindow.document.body.getElementsByTagName("iframe")[0].style.height;
    //             }
    //         }
    //         else
    //         {

    //         }
    //     }
    //     loop_int = setInterval(check, 200);
    // }


    function set_height()
    {
        var name = $(".system_generated_random_name_extension", element).val();
        if (name != "")
        {
            var name_array = name.split(".");
            if (name_array[1])
            {
                if (name_array[1] == "ppt" || name_array[1] == "pptx")
                {
                    //var height = document.getElementsByTagName("iframe")[0].contentWindow.document.body.getElementsByTagName("iframe")[0].style.height;
                    console.log("height");
                    $("iframe", element).height("600px");
                }
            }
        }
    }

    function testset_height()
    {
        console.log("enter testset_height");

        var name = $(".system_generated_random_name_extension", element).text();
        if (name != "")
        {
            console.log("--testset_height has name");
            var name_array = name.split(".");
            if (name_array[1])
            {
                console.log("--testset_height has extension");
                if (name_array[1] == "ppt" || name_array[1] == "pptx")
                {
                    console.log("--testset_height is ppt");
                    $("iframe", element).height("500px");
                }
            }
        }
    }



    // (
    //     function()
    //     {
    //         var handler_url = runtime.handlerUrl(element, "initiate_address");
    //         var baidu_view_proxy_url = runtime.handlerUrl(element, "baidu_view_proxy");

    //         var dict = {
    //             "hello": "world",
    //             "baidu_view_proxy_url":baidu_view_proxy_url,
    //         }

    //         $.ajax
    //         (
    //             {
    //                 type: "POST",
    //                 url: handler_url,
    //                 data: JSON.stringify(dict),
    //                 success: function(responseData)
    //                 {
    //                     $('iframe', element)[0].src = responseData.baidu_view_proxy_url;
    //                     //loop_height();
    //                     set_height();
    //                 },
    //                 error: function(responseData)
    //                 {
    //                     console.log("lms initialization fails!");
    //                 }
    //             }
    //         );
    //     }
    // )();









    /*
        The logic here is to check the status of the document, and then render as needed.
    */

    // function looper()
    // {
    //     var csrfvalue = parse_cookie_and_get_value('csrftoken');
    //     var postUrl = runtime.handlerUrl(element, "check_baidu_upload_status");

    //     $.ajax
    //     (
    //         {
    //             type: "POST",
    //             url: postUrl,
    //             data: JSON.stringify({"hello": "world"}),
    //             beforeSend: function(xhr, settings) 
    //             {
    //                 xhr.setRequestHeader("X-CSRFToken", csrfvalue);
    //             },                   
    //             success: function(response)
    //             {
    //                 if ((response["baidu_processing_status"] == "PUBLISHED") || (response["baidu_processing_status"] == "FAILED"))
    //                 {
    //                     //stop_interval();
    //                     load_doc();
    //                 }
    //             },  
    //             error: function(response)
    //             {
    //                 console.log("--looper Fails");
    //             }
    //         }
    //     )                   
    // }


    // (
    //     function check_status()
    //     {
    //         function looper()
    //         {
    //             console.log("enter looper");
    //             var csrfvalue = parse_cookie_and_get_value('csrftoken');
    //             var postUrl = runtime.handlerUrl(element, "check_baidu_upload_status");

    //             $.ajax
    //             (
    //                 {
    //                     type: "POST",
    //                     url: postUrl,
    //                     data: JSON.stringify({"hello": "world"}),
    //                     beforeSend: function(xhr, settings) 
    //                     {
    //                         xhr.setRequestHeader("X-CSRFToken", csrfvalue);
    //                     },                   
    //                     success: function(response)
    //                     {
    //                         if ((response["baidu_processing_status"] == "PUBLISHED") || (response["baidu_processing_status"] == "FAILED"))
    //                         {
    //                             stop_interval();
    //                             load_doc();
    //                         }
    //                         else
    //                         {
    //                             load_doc();
    //                         }
    //                     },  
    //                     error: function(response)
    //                     {
    //                         console.log("--looper Fails");
    //                     }
    //                 }
    //             )                   
    //         }

    //         function start_interval()
    //         {
    //             interval = setInterval(looper, 500);
    //             return interval;
    //         }

    //         function stop_interval()
    //         {
    //             clearInterval(interval)
    //         }

    //         var interval = null;  
    //         start_interval();
    //     }
    // )();


    /*
        DON'T delete any of the code following since there is a complex logic here, including 3 kinds of state transferring. 

    */

    /*
            Following is the status when we need to check different type of scope variables.
        By experiments, lms and cms don't share any common variables, so it increase the difficulty for variable sharing.
    */
    // function testCountcontent() 
    // {
    //     var handlerUrl = runtime.handlerUrl(element, "increment_countcontent");
    //     $.ajax
    //     (
    //         {
    //             type: "POST",
    //             url: handlerUrl,
    //             data: JSON.stringify({"hello": "world"}),
    //             success: function(responseData)
    //             {
    //                 console.log("right situation");
    //             },
    //         }
    //     );
    // }

    // $(element).find('.increment_countcontent').bind(
    //     'click',
    //     function() 
    //     {
    //         testCountcontent();
    //     }
    // );


    //     function testCountsettings() 
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, "increment_countsettings");
    //         $.ajax
    //         (
    //             {
    //                 type: "POST",
    //                 url: handlerUrl,
    //                 data: JSON.stringify({"hello": "world"}),
    //                 success: function(responseData)
    //                 {
    //                     console.log("right situation");
    //                 },
    //             }
    //         );
    //     }

    // $(element).find('.increment_countsettings').bind(
    //     'click',
    //     function() 
    //     {
    //         testCountsettings();
    //     }
    // );



    //     function testCountuser_state() 
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, "increment_countuser_state");
    //         $.ajax
    //         (
    //             {
    //                 type: "POST",
    //                 url: handlerUrl,
    //                 data: JSON.stringify({"hello": "world"}),
    //                 success: function(responseData)
    //                 {
    //                     console.log("right situation");
    //                 },
    //             }
    //         );
    //     }

    // $(element).find('.increment_countuser_state').bind(
    //     'click',
    //     function() 
    //     {
    //         testCountuser_state();
    //     }
    // );

    //     function testCountpreferences() 
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, "increment_countpreferences");
    //         $.ajax
    //         (
    //             {
    //                 type: "POST",
    //                 url: handlerUrl,
    //                 data: JSON.stringify({"hello": "world"}),
    //                 success: function(responseData)
    //                 {
    //                     console.log("right situation");
    //                 },
    //             }
    //         );
    //     }

    // $(element).find('.increment_countpreferences').bind(
    //     'click',
    //     function() 
    //     {
    //         testCountpreferences();
    //     }
    // );


    // function testCountuser_info() 
    // {
    //     var handlerUrl = runtime.handlerUrl(element, "increment_countuser_info");
    //     $.ajax
    //     (
    //         {
    //             type: "POST",
    //             url: handlerUrl,
    //             data: JSON.stringify({"hello": "world"}),
    //             success: function(responseData)
    //             {
    //                 console.log("right situation");
    //             },
    //         }
    //     );
    // }

    // $(element).find('.increment_countuser_info').bind(
    //     'click',
    //     function() 
    //     {
    //         testCountuser_info();
    //     }
    // );


    // function testCountuser_state_summary() 
    // {
    //     var handlerUrl = runtime.handlerUrl(element, "increment_countuser_state_summary");
    //     $.ajax
    //     (
    //         {
    //             type: "POST",
    //             url: handlerUrl,
    //             data: JSON.stringify({"hello": "world"}),
    //             success: function(responseData)
    //             {
    //                 console.log("right situation");
    //             },
    //         }
    //     );
    // }

    // $(element).find('.increment_countuser_state_summary').bind(
    //     'click',
    //     function() 
    //     {
    //         testCountuser_state_summary();
    //     }
    // );

    // function testfullaccess() 
    // {
    //     console.log("enter testfullaccess");
    //     var csrfvalue = parse_cookie_and_get_value('csrftoken');
    //     var handlerUrl = runtime.handlerUrl(element, "full_access_change_proxy");
    //     $.ajax
    //     (
    //         {
    //             type: "POST",
    //             url: handlerUrl,
    //             data: JSON.stringify({"hello": "world"}),
    //             beforeSend: function(xhr, settings) 
    //             {
    //                 xhr.setRequestHeader("X-CSRFToken", csrfvalue);
    //             }, 

    //             success: function(responseData)
    //             {
    //                 console.log("right situation");
    //             },
    //         }
    //     );
    // }

    // $(element).find('.full_access_change_proxy').bind(
    //     'click',
    //     function() 
    //     {
    //         testfullaccess();
    //     }
    // );


    /*
        Following is fhe original implementation of how to render the page by default, it is now deprecated.

    */

    // /*
    //     Here is to set the link of the download button. 
    // */


    // function set_default_link()
    // {
    //     var baidu_doc_id = $('.baidu_doc_id_input', element).val();

    //     if (baidu_doc_id == "doc-hmqp85mbqpgfxq5")
    //     {
    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $(".download_link")[0].href = "http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61";
    //         }
    //     }
    //     else
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, 'download_proxy');

    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $('.download_link', element)[0].href = handlerUrl;
    //         }
    //         // if ($(".download_link")[0])
    //         // {
    //         //     $(".download_link")[0].href = handlerUrl;
    //         // }
    //         window.handlerUrl = handlerUrl;
    //     }
    // }

    // function test_set_default_link()
    // {
    //     console.log("enter test_set_default_link");

    //     var baidu_doc_id = $('.baidu_doc_id_input', element).val();
    //     console.log("baidu_doc_id is" + baidu_doc_id);

    //     if (baidu_doc_id == "doc-hmqp85mbqpgfxq5")
    //     {
    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $(".download_link",element)[0].href = "http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61";
    //         }         
    //     }
    //     else
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, 'download_proxy');

    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $('.download_link', element)[0].href = handlerUrl;
    //         }

    //         window.handlerUrl = handlerUrl;
    //     }
    // }

    // function set_default_link()
    // {
    //     var baidu_doc_id = $('.baidu_doc_id_input', element).val();

    //     if (baidu_doc_id == "doc-hmqp85mbqpgfxq5")
    //     {
    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $(".download_link")[0].href = "http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61";
    //         }
    //     }
    //     else
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, 'download_proxy');

    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $('.download_link', element)[0].href = handlerUrl;
    //         }
    //         // if ($(".download_link")[0])
    //         // {
    //         //     $(".download_link")[0].href = handlerUrl;
    //         // }
    //         window.handlerUrl = handlerUrl;
    //     }
    // }

    // function test_set_default_link()
    // {
    //     console.log("enter test_set_default_link");

    //     var baidu_doc_id = $('.baidu_doc_id_input', element).val();
    //     console.log("baidu_doc_id is" + baidu_doc_id);

    //     if (baidu_doc_id == "doc-hmqp85mbqpgfxq5")
    //     {
    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $(".download_link")[0].href = "http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61";
    //         }         
    //     }
    //     else
    //     {
    //         var handlerUrl = runtime.handlerUrl(element, 'download_proxy');

    //         if (  $('.download_link', element)[0]  )
    //         {
    //             $('.download_link', element)[0].href = handlerUrl;
    //         }

    //         window.handlerUrl = handlerUrl;
    //     }
    // }

    // /*
    //     Here is to set the link of the iframe. 
    // */
    // function set_default_baidu_doc()
    // {
    //     var handlerUrl = runtime.handlerUrl(element, 'baidu_view_proxy');

    //         // Here we store a hidden button to check the iframe html response is successful or not.
    //         // By default, iframe contains another totally independent html. 
    //         // $(".open_baidu_reader")[0].href = handlerUrl;

    //         // Here we set the address of the iframe to what is desired.
    //         $('iframe', element)[0].src = handlerUrl;
            
    // }

    // function test_set_default_baidu_doc()
    // {
    //     console.log("enter baidu_doc_id");

    //     var baidu_doc_id = $('.baidu_doc_id_input', element).val();
    //     console.log("baidu_doc_id is" + baidu_doc_id);

    //     var handlerUrl = runtime.handlerUrl(element, 'baidu_view_proxy');
    //         // window.baidu_handlerUrl = handlerUrl;

    //         $('iframe', element)[0].src = handlerUrl;
    //         window.iframe_src = handlerUrl;
    // }
    

    // function load_doc() 
    // {
    //         //test_set_default_link();
    //         //test_set_default_baidu_doc();
    //         set_default_link();
    //         set_default_baidu_doc();
    // }


}
