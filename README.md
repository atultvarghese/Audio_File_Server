# Audio_File_Server
CURD on Audio files with FastAPI and MongoDB
Run as
> uvicorn main:app
<h1>Take a look at this docs:</h1>
        <h1>For adding song form_data as</h1>
        {
          "name":"Your song name"
        }
        <h1>For adding podcast form_data as</h1>
        {
          "name":"Your podcast name",
          "host":"Host name",
          "participants":["name1","name2"...]
        }
        <h1>For adding audiobook form_data as</h1>
        {
          "title":"Your audiobook title",
          "author":"Author name",
          "narrator":"Narrator name"
        }
      </code>
      <h1><a href="http://localhost:8000/docs">Click Here for Create/Update/Delete </a></h1>
    </pre>
