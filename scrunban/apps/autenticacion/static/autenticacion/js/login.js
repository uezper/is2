var loginApp = angular.module('loginApp', ['ngCookies']);

/*
  About dependencies:
  0. $scope:    To interact with the form.
  1. $http:     To build our request as ajax requests.
  2. $cookies:  To get the 'csrftoken' in order to validate ours ajax requests.
  3. $window:   To redirect.
  4. $location: To get data from url in order to redirect to a previous requeste page.
*/

loginApp.controller('loginForm', ['$scope', '$http', '$cookies', '$window', '$location', function($scope, $http, $cookies, $window, $location){

    // Prepare header for all AJAX Request
    $http.defaults.headers.common['X-CSRFToken'] = $cookies.get('csrftoken');
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    // Initial message
    $scope.message = '';
    
    $scope.submitData = function(item, event){

	var user = $scope.username;
	var pass = $scope.password;

	// If no data cases
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
		      $scope.message = message;
		      if( status == 'OK' ){
			  defaultDestination = '/'; // Default destination of redirection
			  var destination = $location.search().next;
			  if( destination == undefined ){
			      $window.location.href = defaultDestination;
			  }else{
			      $window.location.href = destination;
			  }
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
