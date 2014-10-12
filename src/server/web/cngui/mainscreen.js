
var gEntities = new Array;    //Index into this with the server ID, Contains full update from server.
var gEntitiesRev = new Array;
var gEntitiesID = new Array;  //Arbitrary list of all server IDs
var gDisplayables = new Array; //index into this with server ID
var gCurrentCameraEye = [10, 10, 10];
var gCurrentCameraAt = [0, 0, 0];
var rootperspective;

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


//Called every frame.
function GameUpdate()
{
	//Update position of all objects.
	//TODO: Tween the motion.
	for (var i in gDisplayables)
	{
		var id = gEntities[i];
		var su = gDisplayables[i];
		su.children[0].matrix.makeIdentity();
		su.children[0].matrix.translate( id.loc );
	}

	//Who are we looking to/from?
	var vf = document.getElementById("viewfrom");
	var vt = document.getElementById("viewto");
	var vfi = vf[vf.selectedIndex].value;
	var vti = vt[vt.selectedIndex].value;

	//vfi/vti.

	var objf = null; if( vfi >= 0 ) objf = gEntities[vfi];
	var objt = null; if( vti >= 0 ) objt = gEntities[vti];

	if( objf == null && objt != null )
	{
		var targ = objt.loc.slice(0);
		var targeye = [ targ[0] + 100, targ[1] + 100, targ[2] + 100 ];

		var slk = .9;
		var islk = 1.-slk;

		gCurrentCameraEye[0] = gCurrentCameraEye[0] * slk + targeye[0] * islk;
		gCurrentCameraEye[1] = gCurrentCameraEye[1] * slk + targeye[1] * islk;
		gCurrentCameraEye[2] = gCurrentCameraEye[2] * slk + targeye[2] * islk;

		gCurrentCameraAt[0] = gCurrentCameraAt[0] * slk + targ[0] * islk;
		gCurrentCameraAt[1] = gCurrentCameraAt[1] * slk + targ[1] * islk;
		gCurrentCameraAt[2] = gCurrentCameraAt[2] * slk + targ[2] * islk;

		//Move the camera to the object.
		rootperspective.at[0] = gCurrentCameraAt[0];
		rootperspective.at[1] = gCurrentCameraAt[1];
		rootperspective.at[2] = gCurrentCameraAt[2];

		rootperspective.eye[0] = gCurrentCameraEye[0];
		rootperspective.eye[1] = gCurrentCameraEye[1];
		rootperspective.eye[2] = gCurrentCameraEye[2];

		rootperspective.up[0] = 0;
		rootperspective.up[1] = 0;
		rootperspective.up[2] = 1;

		rootperspective.angle = 45;

	}
}


