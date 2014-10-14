var cwg; //CNWebGL Context.
var cwgcanvas; //actual HTML5 Canvas.

var rootperspective; //Perspective view.
var rootortho;       //Orthographic view.

var gEntities = new Array;    //Index into this with the server ID, Contains full update from server.
var gEntitiesRev = new Array;
var gEntitiesID = new Array;  //Arbitrary list of all server IDs

var gDisplayables = new Array;
	//index into this with server ID.  
	//This is the actual transform node for the object.

var gCurrentCameraEye = [10, 10, 10];
var gCurrentCameraAt = [0, 0, 0];
var gCurrentCameraUp = [0, 0, 1];
var gCameraFOV = 45;
var gCameraFOVTarget = 45; //Change this for smooth motion.
var gOuterRotateViewX = 0;
var gOuterRotateViewY = 0;
var gViewMode = 0;
	//Mode 0 = view from free, to free.
	//Mode 1 = from free to specific object.
	//Mode 2 = free look from a specific object.
	//Mode 3 = looking from one object to another.

function AddNewObjectDISP( serverID, objparams )
{
	var tt = new CNGLCreateTextureAsset( cwg, serverID + "texture" );
	var tm = new CNGLCreateLoadableModelNode(cwg, serverID + "model" );

	tt.load( "alert1.png" );
	tm.LoadOBJModelURI( "g1.obj");

	o = new CNGLCreateTransformNode(cwg, serverID + "o" );
	su = new CNGLCreateTransformNode(cwg, serverID + "s" );
	o.children.push( tm );
	o.assets.push( tt );
	su.children.push(o);

	gDisplayables[serverID] = su;
	su.matrix.translate( [0,0,0] );
	rootperspective.children.push( su );

	//TODO: Add an ortho icon.
	//Right now we can use an IMG tag.
}

function RemoveObjectDISP( serverID )
{
	//gDisplayables[serverID]
	//XXX TODO actually write this.
}


//Called on new data.
function WSUpdate()
{
	if( !wsDictionary )
	{
		return;
	}

	var wse = wsDictionary.entity;
	if( wse )
	{
		var newEntities = new Array;
		var newEntitiesID = new Array;
		var newEntitiesRev = new Array;

		for( var i = 0; i < wse.length; i++ )
		{
			var id = wse[i].id;
			var vn = " " + id;
			newEntitiesRev[vn] = i;
			newEntitiesID.push( wse[i].id );
			newEntities[id] = wse[i];
		}

		if( gEntities != newEntities )
		{
			gEntities = newEntities;
			gEntitiesRev = newEntitiesRev;
			var eidcopy = gEntitiesID = newEntitiesID;

			//First make sure we don't re-add something.
			var x = document.getElementById("viewfrom");
			var y = document.getElementById("viewto");

			var removeindex = -1;
			for( var i = 0; i < x.options.length; i++ )
			{
				var vn = x.options[i].text;
				var vid = Number( vn.split(':')[0] ); //Server ID

				var io = eidcopy.indexOf( vid );
				if( io >= 0 )
				{
					eidcopy.splice( io, 1 );
				}
				else
				{
					if( x.options[i].value >= 0 && removeindex == -1 )
					{
						//Object does not exist in here.
						//Only can remove one at once.
						removeindex = i;
						RemoveObjectDISP( vid );
					}
				}
			}

			if( removeindex >= 0 )
			{
				x.options.remove( removeindex );
				y.options.remove( removeindex );
			}

			//Add on any things we haven't yet matched.
			for( var i = 0; i < eidcopy.length; i++ )
			{
				var id = eidcopy[i];
				var option = document.createElement("option");
				option.text = id + ":" + "TODO NAME";//gEntities[id];
				option.value = id;
				AddNewObjectDISP( id, /*wse[i].visual*/ "" ); //XXX TODO Need to put in valid visual inforamtion.
				x.options.add( option );

				option = document.createElement("option");
				option.text = id + ":" + "TODO NAME";//gEntities[id];
				option.value = id;
				y.options.add( option );
			}
		}
	}
}

function MouseWheelEvent( direction )
{
	if( gCameraFOVTarget < 90 && direction > 0)
		gCameraFOVTarget++;
	if( gCameraFOVTarget > 1 && direction < 0)
		gCameraFOVTarget--;
}

function MainScreenRelativeRotationMotion( rx, ry )
{
	gOuterRotateViewX += rx * .01;
	gOuterRotateViewY += ry * .01;
	if( gOuterRotateViewY > 1.57 ) gOuterRotateViewY = 1.57;
	if( gOuterRotateViewY < -1.57 ) gOuterRotateViewY = -1.57;
}

//Called every frame.
function GameUpdate()
{
	//Update position of all objects.
	//TODO: Tween the motion.
	for (var i in gDisplayables)
	{
		var id = gEntities[i];
		var su = gDisplayables[i];
		var sc = su.children[0];
		su.matrix.makeIdentity();
		su.matrix.translate( id.loc );
		su.tmphide = false;
		//console.log( sc.screenPlace );
	}

	//Who are we looking to/from?
	var vf = document.getElementById("viewfrom");
	var vt = document.getElementById("viewto");
	var vfi = vf[vf.selectedIndex].value;
	var vti = vt[vt.selectedIndex].value;

	//vfi/vti.

	var objf = null; if( vfi >= 0 ) objf = gEntities[vfi];
	var objt = null; if( vti >= 0 ) objt = gEntities[vti];

	//For smooth motion
	var slk = .9;
	var islk = 1.-slk;

	var targ = gCurrentCameraAt;
	var targeye = gCurrentCameraEye;
	var targup = gCurrentCameraUp;

	if( objf == null && objt == null )
	{
		targ = [ 0, 0, 0];
		targeye = [0, 0, 7000];
		targup = [0, 1, 0];
		gViewMode = 0;
	}
	if( objf == null && objt != null )
	{
		//gOuterRotateViewX
		var dx = 150 * Math.sin(gOuterRotateViewX) * Math.cos( gOuterRotateViewY );
		var dy = 150 * Math.cos(gOuterRotateViewX) * Math.cos( gOuterRotateViewY );
		var dz = 150 * Math.sin( gOuterRotateViewY );
		targ = objt.loc.slice(0);
		targeye = [ targ[0] + dx, targ[1] + dy, targ[2] + dz ];
		targup = [0, 0, 1];
		gViewMode = 1;
	}
	if( objf != null && objt == null )
	{
		var dx = 150 * Math.sin(gOuterRotateViewX) * Math.cos( gOuterRotateViewY );
		var dy = 150 * Math.cos(gOuterRotateViewX) * Math.cos( gOuterRotateViewY );
		var dz = 150 * Math.sin( gOuterRotateViewY );
		targeye = objf.loc.slice(0);
		targ = [ targeye[0] - dx, targeye[1] - dy, targeye[2] - dz ];
		targup = [0, 0, 1];

		//Tricky, we hide the objf so it's not in our face.
		var su = gDisplayables[vfi];
		su.matrix.scale( 0, 0, 0 );
		su.tmphide = true;

		gViewMode = 2;
	}
	if( objf != null && objt != null )
	{
		targ = objt.loc;
		targeye = objf.loc;
		targup = [0, 0, 1];

		//Tricky, we hide the objf so it's not in our face.
		var su = gDisplayables[vfi];
		su.matrix.scale( 0, 0, 0 );
		su.tmphide = true;

		gViewMode = 3;
	}

	gCurrentCameraEye[0] = gCurrentCameraEye[0] * slk + targeye[0] * islk;
	gCurrentCameraEye[1] = gCurrentCameraEye[1] * slk + targeye[1] * islk;
	gCurrentCameraEye[2] = gCurrentCameraEye[2] * slk + targeye[2] * islk;

	gCurrentCameraAt[0] = gCurrentCameraAt[0] * slk + targ[0] * islk;
	gCurrentCameraAt[1] = gCurrentCameraAt[1] * slk + targ[1] * islk;
	gCurrentCameraAt[2] = gCurrentCameraAt[2] * slk + targ[2] * islk;

	gCurrentCameraUp[0] = gCurrentCameraUp[0] * slk + targup[0] * islk;
	gCurrentCameraUp[1] = gCurrentCameraUp[1] * slk + targup[1] * islk;
	gCurrentCameraUp[2] = gCurrentCameraUp[2] * slk + targup[2] * islk;


	//Move the camera to the object.
	rootperspective.at[0] = gCurrentCameraAt[0];
	rootperspective.at[1] = gCurrentCameraAt[1];
	rootperspective.at[2] = gCurrentCameraAt[2];

	rootperspective.eye[0] = gCurrentCameraEye[0];
	rootperspective.eye[1] = gCurrentCameraEye[1];
	rootperspective.eye[2] = gCurrentCameraEye[2];

	rootperspective.up[0] = gCurrentCameraUp[0];
	rootperspective.up[1] = gCurrentCameraUp[1];
	rootperspective.up[2] = gCurrentCameraUp[2];

	gCameraFOV = gCameraFOV * slk + gCameraFOVTarget * islk;
	rootperspective.angle = gCameraFOV;
}


var cwgcq;

function GamePostUpdate()
{

	var tar = document.getElementById('targets');


	for (var i in gDisplayables)
	{
		var id = gEntities[i];
		var su = gDisplayables[i];
		var tarname = "Target"+i;

		var existTarDiv = document.getElementById( tarname );
		if( !existTarDiv )
		{
		console.log( "Adding" );
			existTarDiv = document.createElement('div');
			existTarDiv.setAttribute('id',tarname);
			existTarDiv.setAttribute('class','itarget');
			tar.appendChild(existTarDiv);
		}


		var guard = 10;
		if( (su.screenPlace[0] < 0 || su.screenPlace[1] < 0 ||
			su.screenPlace[0] > cwg.width - guard || su.screenPlace[1] > cwg.height - guard) &&  su.screenPlace[2] >= 1 )
		{
			if( su.screenPlace[0] < 0 ) su.screenPlace[0] = 0;
			if( su.screenPlace[1] < 0 ) su.screenPlace[1] = 0;
			if( su.screenPlace[0] > cwg.width - guard ) su.screenPlace[0] = cwg.width - guard;
			if( su.screenPlace[1] > cwg.height - guard ) su.screenPlace[1] = cwg.height - guard;

			existTarDiv.style.left = (su.screenPlace[0]).toString() + "px";
			existTarDiv.style.top = (su.screenPlace[1]).toString() + "px";
			existTarDiv.style.visibility = "visible";
			existTarDiv.innerHTML = '*';
			//Off the side of the screen
		}
		else if( su.screenPlace[2] >= 1 )
		{
			existTarDiv.style.left = (su.screenPlace[0]-25).toString() + "px";
			existTarDiv.style.top = (su.screenPlace[1]-25).toString() + "px";
			existTarDiv.style.visibility = "visible";
			var ht = "";
			if( su.screenPlace[2] > 300 ) ht += '<img src=target.png>';
			ht += 'ID: ' + i + '<BR>LOC:' + id.loc;
			existTarDiv.innerHTML = ht;
		}
		else
		{
			//Too close.
			existTarDiv.style.visibility = "hidden";			
		}

		//See:
		// su.tmphide
		// su.screenPlace
		//console.log( su.screenPlace );
	}
}


