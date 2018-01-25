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
}
