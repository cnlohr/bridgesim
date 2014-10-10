var camera, scene, renderer;

var ship;
var spin = true;

var mouseX = 0, mouseY = 0;

var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

$(document).ready(function() {
  init();
  animate();
});


function init() {
	camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 2000);
	camera.position.z = 50;

	// scene

	scene = new THREE.Scene();

	var ambient = new THREE.AmbientLight(0x101030);
	scene.add(ambient);

	var directionalLight = new THREE.DirectionalLight(0xffeedd);
	directionalLight.position.set(0, 0, 1);
	scene.add(directionalLight);

	// texture

	var manager = new THREE.LoadingManager();
	manager.onProgress = function (item, loaded, total) {
		console.log(item, loaded, total);
	};

	// model

	var loader = new THREE.OBJLoader(manager);
	loader.load('models/g1.obj', function (object) {
    ship = object;
		scene.add(object);
	});

	//

	renderer = new THREE.WebGLRenderer({canvas: $("#main-canvas").get(0)});
	renderer.setSize(window.innerWidth, window.innerHeight);

	$(document).mousemove(onDocumentMouseMove);

	//

	$(window).resize(onWindowResize);

  $("#center-btn").click(function() { spin = !spin; });
}

function onWindowResize() {
	windowHalfX = window.innerWidth / 2;
	windowHalfY = window.innerHeight / 2;

	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(window.innerWidth, window.innerHeight);
}

function onDocumentMouseMove(event) {
	mouseX = (event.clientX - windowHalfX) / 2;
	mouseY = (event.clientY - windowHalfY) / 2;
}

//

function animate() {
	requestAnimationFrame(animate);
	render();
}

function render() {
	camera.position.x += (mouseX - camera.position.x) * .05;
	camera.position.y += (-mouseY - camera.position.y) * .05;

	camera.lookAt(scene.position);

  if(spin);
    //ship.rotation.y += .01;

	renderer.render(scene, camera);
}

