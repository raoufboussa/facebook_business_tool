var page = require('webpage').create(),

    system = require('system'),

    address, output, size, logoBase64;

// page.paperSize = {
//
//   width: '8in', height: '9.5in',
//
//   orientation: "portrait"
//
// };

if (system.args.length < 3 || system.args.length > 5) {

    console.log('Usage: rasterize.js URL filename [paperwidth*paperheight|paperformat] [zoom]');

    console.log('  paper (pdf output) examples: "5in*7.5in", "10cm*20cm", "A4", "Letter"');

    phantom.exit(1);

} else {

    address = system.args[1];

    output = system.args[2];
    logoBase64 = system.args[3];


  //  page.viewportSize = { width: 1024, height: 770 };

    // if (system.args.length > 3 && system.args[2].substr(-4) === ".pdf") {
    //
    //     size = system.args[3].split('*');
    //
    //     page.paperSize = size.length === 2 ? { width: size[0], height: size[1], margin: '0px' }
    //
    //                                        : { format: system.args[3], orientation: 'portrait', margin: '1cm' };
    //
    // }

    page.paperSize = {
        format: 'A3',
        orientation: 'portrait',
        margin: {
            top: "1.5cm",
            bottom: "1cm"
        },
        header: {
                 height: "1cm",
                 contents: phantom.callback(function(pageNum, numPages) {
                   return "<h4> <span style='float:center'>" + "Gen42 Reports" + "</span></h4><img style='width: 0.95cm; height: 0.95cm' src='"+logoBase64 +"'  />";
                 })
               },
        footer: {
            height: "1cm",
            contents: phantom.callback(function (pageNum, numPages) {
                return '' +
                    '<div style="margin: 0 1cm 0 1cm; font-size: 0.65em">' +
                    '   <div style="color: #888; padding:20px 20px 0 10px; border-top: 1px solid #ccc;">' +
                    '       <span>REPORT FOOTER</span> ' +
                    '       <span style="float:right">' + pageNum + ' / ' + numPages + '</span>' +
                    '   </div>' +
                    '</div>';
            })
        }
    };
    if (system.args.length > 4) {

        page.zoomFactor = system.args[4];

    }
	page.onCallback = function(data){
   if (data.exit) {


   }
};

    page.open(address, function (status) {

        if (status !== 'success') {

            console.log('Unable to load the address!');

            phantom.exit();

        } else {

            window.setTimeout(function () {
				// page.evaluate(function () {
				// 	//document.querySelector(':not(#report42)').remove()
				// //	window.callPhantom({ exit: true }); // callbacks will be called with exit = true
				// 	// console.log(this)
				// });
      //   var checkExist = setInterval(function() {
      //    if (document.querySelector("#report42").length) {
      //       console.log("Exists!");
      //       clearInterval(checkExist);
      //    }
      // }, 100);
      // var clipRect = document.querySelector("#report42").getBoundingClientRect();
      // console.log(clipRect)
      // page.clipRect = {
      //     top:    clipRect.top,
      //     left:   clipRect.left,
      //     width:  clipRect.width,
      //     height: clipRect.height
      // };
        page.render(output)
        phantom.exit();
                // page.render(output);

                //phantom.exit();
				// setTimeout(function () {}, 2000);
				// var clipRect = document.querySelector('#report42').getBoundingClientRect();
				// page.clipRect = {
					// top:    clipRect.top,
					// left:   clipRect.left,
					// width:  clipRect.width,
					// height: clipRect.height
				// };
				//console.log(document.querySelector('#report42'))
				// page.render(output);
				// phantom.exit();

      }, 3100);

        }

    });

}
