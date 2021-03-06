var express = require('express');
var router = express.Router();
var child_process = require('child_process')
var util = require("util");
var bodyParser =    require("body-parser");

var bodyParserUrl = bodyParser.urlencoded();

router.post('/warp', bodyParserUrl, function(req,res){
    var spawn = child_process.spawn;


    // python warpMedia.py [rows] [cols] [mediaId] [x] [y] [w] [h]
    var process = spawn('python',["python/calibration.py", req.body.rows, req.body.cols,
                                req.body.mediaId, req.body.x, req.body.y, req.body.width, req.body.height]);

    process.stdout.on('data',function(chunk){
       var textChunk = chunk.toString('utf8');// buffer to string
       util.log(textChunk);
    });

    process.stderr.on('data', (data) => {
       console.log(`stderr: ${data}`);
    });

    process.on('close', (code) => {
       if(code == 0) {
           res.send( { download: "final/" + req.body.mediaId + ".jpg" } );
           //sendFile( "processed/" + req.file.filename + ".jpg", { root: __dirname } );
       } else {
           return res.status( 403 ).send( "The image provided was not able to be processed. ")
       }
    });
});

module.exports = router;
