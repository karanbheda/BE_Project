var client = new Keen({
  projectId: '5337e28273f4bb4499000000',
  readKey: '8827959317a6a01257bbadf16c12eff4bc61a170863ca1dadf9b3718f56bece1ced94552c6f6fcda073de70bf860c622ed5937fcca82d57cff93b432803faed4108d2bca310ca9922d5ef6ea9381267a5bd6fd35895caec69a7e414349257ef43a29ebb764677040d4a80853e11b8a3f'
});

var geoProject = new Keen({
  projectId: '53eab6e12481962467000000',
  readKey: 'd1b97982ce67ad4b411af30e53dd75be6cf610213c35f3bd3dd2ef62eaeac14632164890413e2cc2df2e489da88e87430af43628b0c9e0b2870d0a70580d5f5fe8d9ba2a6d56f9448a3b6f62a5e6cdd1be435c227253fbe3fab27beb0d14f91b710d9a6e657ecf47775281abc17ec455'
});

Keen.ready(function(){

  $('.users').knob({
    angleArc: 250,
    angleOffset: -125,
    readOnly: true,
    min: 0,
    max: 500,
    fgColor: '#00bbde',
    height: 290,
    width: '95%'
  });

  geoProject
    .query('count_unique', {
      event_collection: 'activations',
      target_property: 'user.id'
    })
    .then(function(res) {
      //$('.users').val(res.result).trigger('change');
    })
    .catch(function(err) {
      alert('An error occurred fetching New Activations metric');
    });


  // ----------------------------------------
  // Errors Detected
  // ----------------------------------------

  $('.errors').knob({
    angleArc:250,
    angleOffset:-125,
    readOnly:true,
    min:0,
    max:100,
    fgColor: '#fe6672',
    height: 290,
    width: '95%'
  });

  geoProject
    .query('count', {
      event_collection: 'user_action',
      filters: [
        {
          property_name: 'error_detected',
          operator: 'eq',
          property_value: true
        }
      ]
    })
    .then(function(res) {
      //$('.errors').val(res.result).trigger('change');
    })
    .catch(function(err) {
      alert('An error occurred fetching Device Crashes metric');
    });


  



initialize();
});
