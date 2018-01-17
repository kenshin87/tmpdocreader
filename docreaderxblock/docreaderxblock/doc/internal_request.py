
import com.baidubce.auth.BceCredentials;
import com.baidubce.auth.SignOptions;
import com.baidubce.http.HttpMethodName;

import com.google.common.collect.Maps;

import org.apache.http.annotation.NotThreadSafe;

import java.net.URI;
import java.util.Map;


class InternalRequest(object):

    def __init__(self):
        parametersDict = {}
        headersDict    = {}
        uri            = None
        httpMethod     = None

        content         = None
        credentials     = None
        signOptions     = None
        expectContinueEnabled = None

        #private RestartableInputStream content;
        #private BceCredentials credentials;
        #private SignOptions signOptions;
        #private boolean expectContinueEnabled;


    def addHeader(self, key, value):
        self.headers[key] = value

    def getHeaders(self):
        return self.headers;


    def addParameter(self, key, value):
        self.parameters[key] = value

    def getParameters(self):
        return self.parameters;

