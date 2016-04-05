var loginApp = angular.module('loginApp', ['ngCookies']);

loginApp.controller('loginForm', ['$scope', '$http', '$cookies', '$window', '$location', function($scope, $http, $cookies, $window, $location){

    // Prepare header for all AJAX Request
    $http.defaults.headers.common['X-CSRFToken'] = $cookies.get('csrftoken');
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    // Initial message
    $scope.message = '';

    $scope.submitData = function(item, event){

	var user = $scope.username;
	var pass = $scope.password;

	if( user === '' || user === undefined ){
	    console.log( 'No username!' );
	    $scope.message = 'Ingrese su usuario!';
	}else if( pass === '' || pass === undefined ){
	    console.log( 'No password' );
	    $scope.message = 'Ingrese su contraseña!';
	}else{
	    $http({method:'POST',
		   url:'authenticate_user/',
		   data: {username: user, password: pass}
		  }).then( function successCallback(response){
		      console.log('We succeded!');
		      message = response['data']['message'];
		      status  = response['data']['STATUS'];
		      console.log(status);
		      if( status == 'OK' ){
			  defaultDestination = '/auth/app/';
			  //var destination = $location.search();
			  //console.log(destination);
			  //console.log(destination['next']);
			  // TODO Get data from next
			  $window.location.href = defaultDestination;
		      }		      
		  }, function errorCallback (response){
		      console.log('We fail!');
		      console.log(response['data']);
		      console.log(response['status']);
		      console.log(response['headers']);
		      console.log(response['config']);
	    });
	}
    }    
}]);

/*
loginApp.controller('noUser', ['$scope', function($scope){
    $scope
}]);*/
