<html>
  <head>
    <title>PyCeed feed configuration: {{filter.name}}</title>
  </head>
  <body>
    <h1>PyCeed feed configuration: {{filter.name}}</h1>
    <form action="{{root}}config/{{filter.name}}" method="post">
      <p>
        Title: <input name="title" type="text" value="{{filter.title}}" />
      </p>
      <p>
        Subtitle: <input name="subtitle" type="text" value="{{filter.subtitle}}" />
      </p>
      <p>
        Definition:<br />
        <textarea rows="15" cols="80" name="definition">{{filter.definition}}</textarea>
      </p>
      <input value="Update feed" type="submit" />
    </form>
  </body>
</html>
