function attachRecommendations(container) {
  if (!container) {
    container = jq('body');
  }
  
  jq('a.recommendAction', container).click(function(event){
    var target = jq(event.target);
    jq.ajax({
      'url': target.attr('href'),
      'data': {'ajax': '1'},
      'type': 'get',
      'dataType': 'html',
      'cache': false,
      'success': function(data, textStatus, jqXHR) {
        if (textStatus == 'success') {
          var html = jq(data);
          attachRecommendations(html);
          target.parent().html(html.find('.recommendAction,.isRecommended'));
        } else {
          alert('Sorry, something went wrong on the server. ' +
            'Please, try a bit later');
        }
        return false;
      },
      'error': function(jqXHR, textStatus, errorThrown) {
        alert('Sorry, something went wrong on the server. ' +
          'Please, try a bit later');
        return false;
      }
    });
    return false;
  });
}

jq(function(){

attachRecommendations();

});
