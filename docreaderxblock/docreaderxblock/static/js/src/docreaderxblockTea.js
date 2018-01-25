    /* Javascript for EncryptedXBlock. */
function DocReaderXBlock(runtime, element) {

/*
    At the very beginning we tried to use our own server as a interchange for file uploading, 
this results in the discrete functions at the very beginning. While it is required to transfer the interchanging mode into 
directly uploading style, then we developed some constructors that wrapped the relative function as classes. This includes:

    1. The client_Temp constructor which handles the uploading process.
    2. The UploadProcessor which tackles the css style of the progress bar.
*/

   var  global = {};
        global.client = null;
        global.baseUrl = "/filecms/image/";
        global.html_element = {
            "user_defined_name": $(".firstXBlockTeaDisplayName"),
            "allow_download": $(".firstxblockAllowDownload"),
            "python_random_name": $(".python_random_name"),
        }

    var gen_util = new GeneralUtil();
    var sts_obj = new TestGetCreDential();
        sts_obj.ajax_get_baidu_sts_xblock();
    var cssValidator = CSSValidator();


function GeneralUtil()
{
    this.copy_dict = function(dict_para)
    {
        var return_dict = {};
        var list = Object.keys(dict_para);
        var length = list.length;
        for (var i = 0; i < length; i++)
        {
            return_dict[list[i]] = dict_para[list[i]];
        }
        return return_dict;
    }

    this.python_compa_file_name = function()
    {
        var random_int = parseInt(Math.random() * 100000) + 100000
        return  +new Date() + "" + random_int;
    }

    this.transfer_element_to_val = function(dict_para)
    {
        var return_dict = {};
        var list = Object.keys(dict_para);
        var length = list.length;
        for (var i = 0; i < length; i++)
        {
            return_dict[list[i]] = dict_para[list[i]].val();
        }
        return return_dict;
    }
    return this;
}

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



function post_file_to_baidu(element_dict_para)
{

    var csrfvalue = parse_cookie_and_get_value('csrftoken');

    var element_val_dict = gen_util.transfer_element_to_val(element_dict_para);

    $(".no_upload_warning", element).text(gettext("正在上传"));  
    $(".no_upload_warning", element).css("color", "#f11");

    var postUrl = runtime.handlerUrl(element, "baidu_upload_proxy");

    var formDataInstance = new FormData();
    
    var user_defined_name   = element_val_dict["user_defined_name"];
    var allow_download = element_val_dict["allow_download"];
    var python_random_name = element_val_dict["python_random_name"];

        formDataInstance.append("user_defined_name", user_defined_name);
        formDataInstance.append("allow_download", allow_download);
        formDataInstance.append("python_random_name", python_random_name);

    $.ajax
    (
        {
            type : "POST",
            url  : postUrl,
            data : formDataInstance,
            cache: false,
            async: false,
            contentType: false,
            processData: false,
            beforeSend: function(xhr, settings) 
            {
                xhr.setRequestHeader("X-CSRFToken", csrfvalue);
            }, 
            success: function(response)
            {
                runtime.notify('save', {state: 'end'});
            },  

            error: function(response)
            {
                console.log("--postFileToCMS Fails");
                $(".no_upload_warning", element).css("color", "#f11");
            }
        }
    )
}


function  CSSValidator(sts_obj)
{
    var obj = {};

    obj.check_file_exists = function(event_object)
    {
         if ( $("#file", element)[0].files.length != 0 )
         {
            return true;
         }
         else
         {
            return false;
         }
    }

    obj.check_valid_format = function(event_object)
    {
        if ( $("#file", element)[0].files.length != 0 )
        {   
            var soloFile = $("#file", element)[0].files[0];
            var nameList  = soloFile.name.split(".");
            var available = {"pdf":"pdf", "xls":"xls", "xlsx":"xlsx", "doc":"doc", "docx":"docx", "ppt":"ppt", "pptx":"pptx"}; 
       
            if (
                    nameList.length < 2
                        ||  
                    (!(nameList[nameList.length - 1].toLowerCase() in available))
               )
            {
                event_object.preventDefault();
                $(".no_upload_warning", element).css("color", "#f11")
                $(".no_upload_warning", element).text(gettext("只支持ppt, excel, word, pdf文件的上传！"));
                return false;
            }
        }     
        return true;
    }

    obj.check_valid_size = function(event_object)
    {
        if ( $("#file")[0].files.length != 0 )
        {
            var soloFile = $("#file", element)[0].files[0];
            var size = soloFile.size;
            if (size > 1024 * 1024 * 95)
            {
                event_object.preventDefault();
                $(".no_upload_warning", element).css("color", "#f11");
                $(".no_upload_warning", element).text(gettext("无法上传超过100ｍ的文件!"));  
                return false;              
            }            
        }
        return true;
    }
    return obj;
}



function client_Temp(sts_obj)
{

    var obj = {};
        obj.python_random_name = $(".python_random_name");

        obj.sts_obj = sts_obj;
    var upload_obj = new UploadProcessor();
    var config =  sts_obj.config;

    var bosConfig = {
        credentials: {
             ak: config.bos_sts_ak,
             sk: config.bos_sts_sk,
             
         },
         sessionToken: config.bos_sts_token,
         endpoint: config.bos_endpoint, // 
     };


    obj.upload = function()
    {
        var bucket = config.bos_bucket_name; // 设置您想要操作的bucket
        var client = new baidubce.sdk.BosClient(bosConfig);

        client.on('progress', 
            function (event)
            {
                if (event.lengthComputable)
                {
                    var percentage = (event.loaded / event.total) * 100;
                    upload_obj.upload_progress_handler(event);
                }
            }
        );

        var file = $("#file")[0].files[0]; // 获取要上传的文件
        var file_name_list = file.name.split(".");
        var extention = file_name_list[file_name_list.length - 1];
        var key = gen_util.python_compa_file_name() + "." + extention;
        obj.python_random_name.val(key); 
        var blob = file;

        var ext = key.split(/\./g).pop();
        var mimeType = baidubce.sdk.MimeType.guess(ext);
        if (/^text\//.test(mimeType)) 
        {
            mimeType += '; charset=UTF-8';
        }
        var options = 
        {
            'Content-Type': mimeType
        };

        client.putObjectFromBlob(bucket, key, blob, options)
        .then(
            function (res) 
            {
                post_file_to_baidu(global.html_element);
            })
        .catch(
            function (err) 
            {
                console.log(err);
            });        
    }
    return obj;
};



function UploadProcessor()
{
    var obj = {};

    obj.width = 0.68;

    obj.input_button  = document.getElementById("file");
    obj.submit_button = document.getElementById("baidu_submit");

    obj.set_bar_P_up_width = function(event)
    {
        
        document.getElementById("progress_bar_p_up").style.width = obj.get_percentage(event).toFixed(2) * obj.width + "%";
        //console.log(obj.get_percentage(event).toFixed(2) * obj.width  + "%");
        //document.getElementById("progress_bar_p_up").style.width = obj.get_percentage(event).toFixed(2) * obj.width / 100 + "px";
    }

    obj.set_span_value = function(event)
    {
        document.getElementById("progress_value_span").innerHTML = obj.get_percentage(event).toFixed(2) + "%";
    }

    obj.disable_button_style = function()
    {
        obj.submit_button.disabled = true;


        obj.input_button.disabled = true;
         
    }

    obj.enable_button_style = function()
    {
        obj.submit_button.disabled = false;


        obj.input_button.disabled = false;
         
    }

    obj.get_percentage = function (event)
    {
        /*
            Why we want to put the button style inside the get_percentage function, is that the re-enable function is determined by the 
        get_percentage function, so here we wrap the function inside get_percentage.
        */
        obj.disable_button_style();
        var value = event.loaded/event.total;
        if (value == 1)
        {
            obj.enable_button_style();
        }
        return event.loaded/event.total * 100;
    }
    obj.upload_progress_handler = function (event)
    {
        /*
            There are 2 things that we need to do:
                1. change the value of the uploading progress
                2. change the width of the color bar.
        */
        obj.set_span_value(event);
        obj.set_bar_P_up_width(event);
        //console.log(obj.get_percentage(event));
    }


    obj.full_upload = function()
    {
        var eve = {};
        eve.loaded = 100;
        eve.total  = 100;
        obj.set_span_value(eve);
        obj.set_bar_P_up_width(eve);
        obj.enable_button_style();
    }

    obj.transfer_event = function(event)
    {
        event.loaded = event._loadedBytes;
        event.total = event._totalBytes;
        return event;
    }
    return obj;
}


function TestGetCreDential()
{
    var obj = {};

        obj.refresh_current_config = function()
        {
            obj.config = {
                "bos_bucket_name": obj.bos_bucket_name.val(),
                "bos_sts_ak": obj.bos_sts_ak.val(),
                "bos_sts_sk": obj.bos_sts_sk.val(),
                "bos_sts_token": obj.bos_sts_token.val(),
                "bos_endpoint": obj.end_point.val(),
            }
            return obj.config;
        }

        obj.bos_bucket_name = $(".bos_bucket_name");
        obj.bos_sts_ak = $(".bos_sts_ak");
        obj.bos_sts_sk = $(".bos_sts_sk");
        obj.bos_sts_token = $(".bos_sts_token");
        obj.end_point = $(".bos_endpoint");

        obj.config = obj.refresh_current_config();


    obj.ajax_get_baidu_sts_xblock = function()
    {

        var jsonData = JSON.stringify(
            {
                "bucket_name": obj.bos_bucket_name.val(), 
            }
        );
        var postUrl = runtime.handlerUrl(element, "get_baidu_sts");

        $.ajax
        (
            {
                type: "POST",
                url: postUrl,
                data: jsonData,
                success: function(response)
                {
                    obj.set_name(response);
                    obj.refresh_current_config();
                },  

                error: function(response)
                {
                    console.log("--testget_baidu_sts Fails");
                }
            }
        ) 
    }

    obj.testajax_get_baidu_sts_xblock = function()
    {

        var jsonData = JSON.stringify(
            {
                "bucket_name": $(".bos_bucket_name").val(), 
            }
        );
        var postUrl = runtime.handlerUrl(element, "get_baidu_sts");

        $.ajax
        (
            {
                type: "POST",
                url: postUrl,
                data: jsonData,
                success: function(response)
                {
                    //console.log("--testget_baidu_sts success");
                    obj.set_name(response);
                    obj.refresh_current_config();
                },  

                error: function(response)
                {
                    console.log("--testget_baidu_sts Fails");
                }
            }
        ) 
    }

    obj.ajax_get_baidu_sts = function()
    {
        $.ajax
        (
            {
                type: "GET",
                async: false,
                url: "http://127.0.0.1:8000/courses/course-v1:EliteU+11067001+A1/yingliapi/get_baidu_temp_sts?bucket_name=" + obj.bos_bucket_name.val(),

                success: function(response)
                {
                    obj.set_name(response);
                    obj.refresh_current_config();
                },  

                error: function(response)
                {
                    console.log("--testget_baidu_sts Fails");
                }
            }
        )        
    }

    obj.testajax_get_baidu_sts = function()
    {
        $.ajax
        (
            {
                type: "GET",
                async: false,
                url: "http://127.0.0.1:8000/courses/course-v1:EliteU+11067001+A1/yingliapi/get_baidu_temp_sts?bucket_name=" + obj.bos_bucket_name.val(),

                success: function(response)
                {
                    console.log("--testget_baidu_sts success");
                    window.testget_baidu_sts_data = response;
                    obj.set_name(response);
                    obj.refresh_current_config();
                },  

                error: function(response)
                {
                    console.log("--testget_baidu_sts Fails");
                }
            }
        )        
    }

    obj.get_regular_object = function(baidu_response_dict)
    {
        var regular_object = {};

            regular_object["bos_sts_ak"] = baidu_response_dict["accessKeyId"];
            regular_object["bos_sts_sk"] = baidu_response_dict["secretAccessKey"];
            regular_object["bos_sts_token"] = baidu_response_dict["sessionToken"];

        return regular_object;     
    }

    obj.set_name = function(baidu_response_dict)
    {
        var regular_object = obj.get_regular_object(baidu_response_dict);

        obj.bos_sts_ak.val(regular_object["bos_sts_ak"]);
        obj.bos_sts_sk.val(regular_object["bos_sts_sk"]);
        obj.bos_sts_token.val(regular_object["bos_sts_token"]);
    }

    return obj;
}

function check_valid_name(event_object)
{
    // return true when there is no need to check whether the name is valid or not.
    return true;

    //Assure that a name is offered.
    if ( $(".firstXBlockTeaDisplayName", element).val() == "文档预览")
    {
        event_object.preventDefault();
        $(".noFileNameWarning", element).css("color", "#f11")
        $(".noFileNameWarning", element).text(gettext("请先更改文档的文件名"));
        return false;
    }
    return true;
}

function testcheck_valid_name(event_object)
{
    console.log("enter testcheckValidName");
    return true;
    //Assure that a name is offered.
    if ( $(".firstXBlockTeaDisplayName", element).val() == "文档预览" )
    {
        event_object.preventDefault();
        $(".noFileNameWarning", element).css("color", "#f11")
        $(".noFileNameWarning", element).text(gettext("请先更改文档的文件名"));
        console.log("--testcheckValidName is false");
        return false;
    }
    console.log("--testcheckValidName is true");
    return true;
}

function checkFileExists(event_object)
{
     if ( $(".file-upload")[0].files.length != 0 )
     {
        return true;
     }
     else
     {
        return false;
     }
}

function testcheckFileExists(event_object)
{
    console.log("enter testcheckFileExists");

     if ( $(".file-upload", element)[0].files.length != 0 )
     {
        console.log("--testcheckFileExists true");
        return true;
     }
     else
     {
        console.log("--testcheckFileExists false");
        return false;
     }
}

function checkValidSize(event_object)
{
    if ( $(".file-upload", element)[0].files.length != 0 )
    {
        var soloFile = $(".file-upload", element)[0].files[0];
        var size = soloFile.size;
        if (size > 1024 * 1024 * 95)
        {
            event_object.preventDefault();
            $(".no_upload_warning", element).css("color", "#f11");
            $(".no_upload_warning", element).text(gettext("无法上传大小超过90M的文件!"));  
            return false;              
        }            
    }
    return true;
}

function testcheckValidSize(event_object)
{
    console.log("enter testcheckValidSize");
    if ( $(".file-upload", element)[0].files.length != 0 )
    {
        var soloFile = $(".file-upload", element)[0].files[0];
        var size = soloFile.size;
        if (size > 1024 * 1024 * 95)
        {
            event_object.preventDefault();
            $(".no_upload_warning", element).css("color", "#f11")
            $(".no_upload_warning", element).text(gettext("无法上传大小超过90M的文件!"));  
            console.log("--testcheckValidSize is False");
            return false;              
        }            
    }
    console.log("--testcheckValidSize is true");
    return true;
}

function checkValidFormat(event_object)
{
    if ( $(".file-upload", element)[0].files.length != 0 )
    {   
        var soloFile = $(".file-upload", element)[0].files[0];
        var nameList  = soloFile.name.split(".");
        var available = {"pdf":"pdf", "xls":"xls", "xlsx":"xlsx", "doc":"doc", "docx":"docx", "ppt":"ppt", "pptx":"pptx"}; 
   
        if (
                nameList.length < 2
                    ||  
                (!(nameList[nameList.length - 1].toLowerCase() in available))
           )
        {
            event_object.preventDefault();
            $(".no_upload_warning", element).css("color", "#f11")
            $(".no_upload_warning", element).text(gettext("只支持ppt, excel, word, pdf文件的上传！"));
            return false;
        }
    }     
    return true;
}

function testcheckValidFormat(event_object)
{
    console.log("enter testcheckValidFormat");
    if ( $(".file-upload", element)[0].files.length != 0 )
    {   
        var soloFile = $(".file-upload", element)[0].files[0];
        var nameList  = soloFile.name.split(".");
        var available = {"pdf":"pdf", "xls":"xls", "xlsx":"xlsx", "doc":"doc", "docx":"docx", "ppt":"ppt", "pptx":"pptx"}; 
   
        if (
                nameList.length < 2
                    ||  
                (!(nameList[nameList.length - 1].toLowerCase() in available))
           )
        {
            event_object.preventDefault();
            $(".no_upload_warning", element).css("color", "#f11")
            $(".no_upload_warning", element).text(gettext("只支持ppt, excel, word, pdf文件的上传！"));
            return false;
        }
    }
    return true;       
}

function checkWhetherValidChangeName(event_object)
{
    // // It means that the user has not uploaded any file bofore.
    // if ( $(".baidu_doc_id", element).val() == "doc-hmqp85mbqpgfxq5" )
    // {
    //         event_object.preventDefault();
    //         $(".no_upload_warning", element).css("color", "#f11")
    //         $(".no_upload_warning", element).text("请先上传一个合法文件！");
    // }
    // // It means that the user has uploaded some files.
    // else
    // {
        changeName();
    // }
}

function testcheckWhetherValidChangeName(event_object)
{
    // console.log("enter testcheckWhetherValidCheckName");

    // // It means that the user has not uploaded any file bofore.
    // if ( $(".baidu_doc_id", element).val() == "doc-hmqp85mbqpgfxq5" )
    // {
    //         event_object.preventDefault();
    //         $(".no_upload_warning", element).css("color", "#f11")
    //         $(".no_upload_warning", element).text("请先上传一个合法文件！");
    // }

    // // It means that the user has uploaded some files.
    // else
    // {
        testchangeName();
    // }
}

    // By posting a formdata instance including a file to the server, it get the randomized file name 

    // require:
    //     <input class = "systemGeneratedRandomName" value = {self.systemGeneratedRandomName}    
    //     <input class = "file-upload" name  = "file-upload"   >
    //     <input class = "ajaxFileServer">
    // return:
    //     randomized file name of the pdf file, aka "32498753958234958.pdf"

    $(element).find('.cancel-button').bind('click', function() {
        runtime.notify('cancel', {});
    });

    

    $(element).find('.save-button').bind
    (
        'click', 
        //testajax_upload_wrapper
        //ajax_upload_wrapper
        wrapper_chooser
        //testwrapper_chooser
    );

    function wrapper_chooser(event_object)
    {
        event_object.preventDefault();

        if ( $("#file")[0].files.length != 0 )
        {
            baidu_upload_wrapper(event_object);
        }    
        else
        {
            return ajax_upload_wrapper(event_object);
        }
    }

    function testwrapper_chooser(event_object)
    {
        console.log("enter wrapper_chooser");
        event_object.preventDefault();

        if ( $("#file")[0].files.length != 0 )
        {
            testbaidu_upload_wrapper(event_object);
        }    
        else
        {
            return ajax_upload_wrapper(event_object);
        }
    }


$('#baidu_submit').click(
function (event) 
{
    event.preventDefault();
    if (global.client == null)
    {
        //console.log("global.client is null");
        global.client = new client_Temp(sts_obj);
    }
    $("#progress_bar_div").css({"display":"inline-block"});
    global.client.upload();
    return false;
});

// $('#file').change(
// function () 
// {
//     $("#progress_bar_div").css({"display":"inline-block"});
// });

    function baidu_upload_wrapper(event_object)
    {
            if (!cssValidator.check_valid_size(event_object))
            {
                return;
            }     
            
            if (!cssValidator.check_valid_format(event_object))
            {
                return;
            }     
            $('#baidu_submit').click();
    }

    function testbaidu_upload_wrapper(event_object)
    {
            if (!cssValidator.check_valid_size(event_object))
            {
                return;
            }     
            
            if (!cssValidator.check_valid_format(event_object))
            {
                return;
            }     
            console.log("passed test"); 
            $('#baidu_submit').click(); 
            //event_object.preventDefault();
    }


    function ajax_upload_wrapper(event_object)
    {
        if (!check_valid_name(event_object))
        {
            return;
        }     

        if (checkFileExists(event_object))
        {
            if (!checkValidSize(event_object))
            {
                return;
            }     
            
            if (!checkValidFormat(event_object))
            {
                return;
            }       
            event_object.preventDefault();
            postFileToCMS();
        }
        else
        {
            // TODO: should not return, here need to be further implemented.
            // This is the case when the teacher want to change the name of the file.
            event_object.preventDefault();
            checkWhetherValidChangeName(event_object); 
        }
    }

    function testajax_upload_wrapper(event_object)
    {
        if (!check_valid_name(event_object))
        {
            console.log("testcheckValidName fails.");
            return;
        }     

        if (testcheckFileExists(event_object))
        {
            if (!testcheckValidSize(event_object))
            {
                console.log("testcheckValidSize fails.");
                return;
            }
            if (!testcheckValidFormat(event_object))
            {
                console.log("testcheckValidFormat fails.");
                return;
            }       
            event_object.preventDefault();
            testpostFileToCMS();
        }
        else
        {
            // This is the case when the teacher want to change the name of the file, or 
            event_object.preventDefault();
            testcheckWhetherValidChangeName(event_object);
        }
    }


    function postFileToCMS()
    {
        $(".no_upload_warning", element).text(gettext("文件正在上传中，请耐心等待。"));  
        $(".no_upload_warning", element).css("color", "#f11");
        runtime.notify('save', {state: 'start'});

        var postUrl = runtime.handlerUrl(element, "upload_proxy");

        var formDataInstance = new FormData();
            formDataInstance.append("file-upload", $(".file-upload", element)[0].files[0]);
        
        var user_defined_name   = $(".firstXBlockTeaDisplayName", element).val();
        var allow_download = $(".firstxblockAllowDownload", element).val();

            formDataInstance.append("user_defined_name", user_defined_name);
            formDataInstance.append("allow_download", allow_download);


        $.ajax
        (
            {
                type : "POST",
                url  : postUrl,
                data : formDataInstance,
                cache: false,
                async: false,
                contentType: false,
                processData: false,

                success: function(response)
                {
                    runtime.notify('save', {state: 'end'});
                },  

                error: function(response)
                {
                    console.log("--postFileToCMS Fails");
                    $(".no_upload_warning", element).css("color", "#f11");
                }
            }
        )
    }

    function testpostFileToCMS()
    {
        $(".no_upload_warning", element).text(gettext("文件正在上传中，请耐心等待。"));  
        $(".no_upload_warning", element).css("color", "#f11");
        
        runtime.notify('save', {state: 'start'});

        console.log("enter testpostFileToCMS");
        var postUrl = runtime.handlerUrl(element, "upload_proxy");

        var formDataInstance = new FormData();
        formDataInstance.append("file-upload", $(".file-upload", element)[0].files[0]);

        var user_defined_name   = $(".firstXBlockTeaDisplayName", element).val();
        var allow_download = $(".firstxblockAllowDownload", element).val();

            formDataInstance.append("user_defined_name", user_defined_name);
            formDataInstance.append("allow_download", allow_download);

        $.ajax
        (
            {
                type : "POST",
                url  : postUrl,
                data : formDataInstance,
                cache: false,
                async: false,
                contentType: false,
                processData: false,

                success: function(response)
                {
                    runtime.notify('save', {state: 'end'});
                    console.log("--testpostFileToCMS success");
                    window.testpostFileToCMS_data = response;
                },  

                error: function(response)
                {
                    console.log("--testpostFileToCMS Fails");
                    $(".no_upload_warning", element).css("color", "#f11");
                }
            }
        )
    }

    // Argument response here is just a string of " {"result": {"file_url": "asdasdasd.pdf"}} "
    function changeName(event_object) 
    {
        runtime.notify('save', {state: 'start'});

        var postUrl = runtime.handlerUrl(element, "renewName");
        var user_defined_name   = $(".firstXBlockTeaDisplayName", element).val();
        var allow_download = $(".firstxblockAllowDownload", element).val();


        var jsonData = JSON.stringify(
                {
                    "user_defined_name": user_defined_name, 
                    "allow_download": allow_download,
                }
            );

        $.ajax
        (
            {
                type: "POST",
                url: postUrl,
                data: jsonData,
                success: function(response)
                {
                    runtime.notify('save', {state: 'end'});                    
                },  
                error: function(response)
                {
                    console.log("--testchangeName Fails");
                    $(".no_upload_warning", element).css("color", "#f11");
                }
            }
        )
    }

    // Argument response here is just a string of " {"result": {"file_url": "asdasdasd.pdf"}} "
    function testchangeName(event_object) 
    {
        runtime.notify('save', {state: 'start'});

        console.log("enter testchangeName");

        var postUrl = runtime.handlerUrl(element, "renewName");

        var user_defined_name   = $(".firstXBlockTeaDisplayName", element).val();
        var allow_download = $(".firstxblockAllowDownload", element).val();


        var jsonData = JSON.stringify(
                {
                    "user_defined_name": user_defined_name, 
                    "allow_download": allow_download,
                }
            );

        $.ajax
        (
            {
                type: "POST",
                url: postUrl,
                data: jsonData,
                success: function(response)
                {
                    runtime.notify('save', {state: 'end'});
                    console.log("--testchangeName success");
                    window.testchangeName_data = response;

                },  

                error: function(response)
                {
                    console.log("--testchangeName Fails");
                    $(".no_upload_warning", element).css("color", "#f11");
                }
            }
        )
    }
}

