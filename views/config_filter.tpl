<!DOCTYPE HTML>
<!--
#  This file is part of PyCeed.
#
#  PyCeed is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  PyCeed is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PyCeed.  If not, see <http://www.gnu.org/licenses/>.
-->
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
