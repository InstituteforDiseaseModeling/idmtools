const proxy = require('http-proxy-middleware');



module.exports = function(app) {

    const serviceName =  process.env.REACT_APP_SERVICE  || "localhost"

    app.use(proxy('/api',
        {
            "target": "http://" + serviceName +":5000",
            // "pathRewrite": {
            //     "^/api": ""
            // }
        }

    ));

    // app.use(proxy('/data',
    // {
    //     "target": "file:///home/dkong/source/idmtools",
    //     "pathRewrite": {
    //         "^/data": "/data/workers"
    //     }
    // }
  //));


};


