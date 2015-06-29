<html>
  <head>
    <title>PyCeed feeds configuration</title>
    %if filters:
    <script>
      function select_new() {
        document.getElementById("cn_new").checked = true;
      }
    </script>
    %end
  </head>
  <body>
    <h1>PyCeed feeds configuration</h1>
    <p>Please choose a feed configuration or type a feed name</p>
    <form action="{{root}}config" method="post">
      <p>
        %if filters:
        %for filter in filters:
        <input type="radio" name="config_name" value="{{filter.name}}" />{{filter.name}}<br />
        %end
        <br />
        <input type="radio" name="config_name" id="cn_new" value="_new" />New feed: <input name="config_name_text" type="text" onkeydown="select_new();" oncut="select_new();" onpaste="select_new();" /><br />
        %else:
        <input name="config_name_text" type="text" />
        %end
      </p>
      <input value="View feed" type="submit" />
    </form>
  </body>
</html>
