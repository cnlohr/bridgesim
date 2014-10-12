//In order to use this, you must have the following functions:
//
//Mouse wheel:
//		AttachMouseWheel( MouseWheelEvent, ObjectThatWeAttachToLikeACanvas ); 
// where MouseWheelEvent is function( inout ) -> where inout = -1 or +1 depending on scroll direction.
// call this after main boots.
//
//Full screen:
// goFullScreen( requestingDiv )
//
//Pointer motion:
// setupPoinerMotion( PointerMotionFn )
// where PointerMotionFn( x, y, relx, rely, buttons, locked )
//


function goFullScreen( te){
    if(te.requestFullScreen)
        te.requestFullScreen();
    else if(te.webkitRequestFullScreen)
        te.webkitRequestFullScreen();
    else if(te.mozRequestFullScreen)
        te.mozRequestFullScreen();
}




//Pointer locking: http://www.html5rocks.com/en/tutorials/pointerlock/intro/

var ispointerlocked = false;
var PointerMotionFn;
var clickerbutton = false;

var ptrabsx = 0;
var ptrabsy = 0;

/*function bodymove( ev )
{
	var x = ev.clientX;
	var y = ev.clientY;
}*/

function setupPoinerMotion( PointerFn )
{
	PointerMotionFn = PointerFn;
	document.addEventListener("mousemove", fsmm, false);
	document.addEventListener("mousedown", fsmmd, false);
	document.addEventListener("mouseup", fsmmu, false);
}

function LockchangeCallback( j )
{
//	console.log( "Changed: " );
//	console.log( document.mozPointerLockElement );
	if( document.mozPointerLockElement != null ||
		document.webkitPointerLockElement != null || 
		document.PointerLockElement != null )
	{
		ispointerlocked = true;
	} 
	else
	{
		ispointerlocked = false;
	}
}

function fsmmu()
{
	clickerbutton = false;
	PointerMotionFn( ptrabsx, ptrabsy, 0, 0, clickerbutton, ispointerlocked );
	return false;
}
function fsmmd()
{
	clickerbutton = true;
	PointerMotionFn( ptrabsx, ptrabsy, 0, 0, clickerbutton, ispointerlocked );
	return false;
}

function fsmm( e )
{
  var movementX = e.movementX ||
      e.mozMovementX          ||
      e.webkitMovementX       ||
      0,
  movementY = e.movementY ||
      e.mozMovementY      ||
      e.webkitMovementY   ||
      0;

	ptrabsx += movementX;
	ptrabsy += movementY;

	PointerMotionFn( ptrabsx, ptrabsy, movementX, movementY, clickerbutton, ispointerlocked );
	return false;
}


function pointerlock( lock, element )
{
	// Hook pointer lock state change events
	document.addEventListener('pointerlockchange', LockchangeCallback, false);
	document.addEventListener('mozpointerlockchange', LockchangeCallback, false);
	document.addEventListener('webkitpointerlockchange', LockchangeCallback, false);

	// Hook mouse move events
	document.addEventListener("mousemove", fsmm, false);

	//http://www.html5rocks.com/en/tutorials/pointerlock/intro/
	var havePointerLock = 'pointerLockElement' in document ||
	    'mozPointerLockElement' in document ||
	    'webkitPointerLockElement' in document;

	if( !havePointerLock )
	{
		console.log( "Does not have pointer lock functionality in this browser.\n" );
		return;
	}

	if( lock )
	{
		element.requestPointerLock = element.requestPointerLock ||
				     element.mozRequestPointerLock ||
				     element.webkitRequestPointerLock;
		// Ask the browser to lock the pointer
		element.requestPointerLock();
		ispointerlocked = true;
	}
	else
	{
		// Ask the browser to release the pointer
		document.exitPointerLock = document.exitPointerLock ||
				   document.mozExitPointerLock ||
				   document.webkitExitPointerLock;
		document.exitPointerLock();
		ispointerlocked = false;
	}
}



//Zoom in/out  (Mouse wheel)

function mousewheelhandlerroot(e){
    var evt=window.event || e;
    var delta=evt.detail? evt.detail*(-120) : evt.wheelDelta;
    var direction = (delta<=-120)?1:-1;

	mwevlocal( direction );
}

function AttachMouseWheel( inoutfunction, canv )
{
	var mousewheelevt=(/Firefox/i.test(navigator.userAgent))? "DOMMouseScroll" : "mousewheel" //FF doesn't recognize mousewheel as of FF3.x

	if (canv.attachEvent) //if IE (and Opera depending on user setting)
		canv.attachEvent("on"+mousewheelevt, mousewheelhandlerroot)
	else if (canv.addEventListener) //WC3 browsers
		canv.addEventListener(mousewheelevt, mousewheelhandlerroot, false)
	mwevlocal = inoutfunction;
}

