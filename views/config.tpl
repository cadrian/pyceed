<html>
  <head>
    <title>PyCeed feeds configuration</title>
    %if filters:
    <script>
      function select_new() {
        document.getElementById("config_name").value = "_new";
      }
    </script>
    %end
  </head>
  <body>
    <h1>PyCeed feeds configuration</h1>
    <p>Please choose a feed configuration or type a feed name</p>
    <form action="{{root}}config" method="post">
      %if filters:
      <ul>
        <select name="config_name" size="{{len(filters) + 1}}">
          %for filter in filters:
          <li><option value="{{filter.name}}">{{filter.name}}</option></li>
          %end
          <li><option value="_new"><input name="config_name_text" type="text" onkeydown="select_new();" oncut="select_new();" onpaste="select_new();"/></option></li>
        </select>
      </ul>
      %else:
      <p>
        <input name="config_name_text" type="text" />
      </p>
      %end
      <input value="View feed" type="submit" />
    </form>
  </body>
</html>
