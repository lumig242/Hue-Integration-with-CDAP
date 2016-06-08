<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("cdap", "cdap", user) | n,unicode}
${shared.menubar(section='mytab')}

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/themes/default/style.min.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-jsonview/1.2.3/jquery.jsonview.css">
<link rel="stylesheet" href="/static/cdap/css/cdap.css">

<style>

</style>

## Use double hashes for a mako template comment
## Main body

<div class="modal fade" id="popup" role="dialog">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal">&times;</button>
      <h4 class="modal-title">Login to secure cdap cluster</h4>
    </div>
    <div class="modal-body">
        <label for="cdap_username">Name:</label>
      <input id="cdap_username" type="text"/>
        <label for="cdap_password">Password:</label>
        <input id="cdap_password" type="password"/>
    </div>
    <div class="modal-footer">
      <button onclick="cdap_submit()" type="button" class="btn btn-default" data-dismiss="modal">Login</button>
    </div>
</div>

<div class="modal fade" id="new-acl-popup" role="dialog">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal">&times;</button>
      <h4 class="modal-title">Configure the ACL</h4>
    </div>
    <div class="modal-body">
        <label for="role">Select a role:</label>
        <select name="user-group" id="role" class="user-group">
            </select><br/>
        <label class="checkbox inline-block">
            <input type="checkbox" data-bind="checked: read" value="READ">
            Read <span class="muted">(r)</span>
        </label>
        <label class="checkbox inline-block">
            <input type="checkbox" data-bind="checked: write" value="WRITE">
            Write <span class="muted">(w)</span>
        </label>
                                        <label class="checkbox inline-block">
            <input type="checkbox" data-bind="checked: execute" value="EXECUTE">
            Execute <span class="muted">(x)</span>
        </label>
                    <label class="checkbox inline-block">
            <input type="checkbox" data-bind="checked: admin" value="ADMIN">
            ADMIN <span class="muted">(admin)</span>
        </label>
                    <label class="checkbox inline-block">
            <input type="checkbox" data-bind="checked: all" value="ALL">
            All <span class="muted">(all)</span>
        </label>
    </div>
    <div class="modal-footer">
      <button onclick="saveACL()" type="button" class="btn btn-default" data-dismiss="modal">Save</button>
    </div>
</div>

<div class="container-fluid">
  <div class="card">
    <h2 class="card-heading simple">Entities</h2>
    <div class="card-body">
        % if unauthenticated:
            <h1>You are not authorized!</h1>
            <p hidden class="is_authenticated">False<p>
        % else:
        <div class="row-fluid">

            <div class="span8">
            <div id="jstree">
     <ul>
        <li> Namespaces
        % for name, namespace in entities.iteritems():
        <ul>
          <li>${name}
            <ul>
                % for key, value in namespace.iteritems():
                    % if value:
                        <li> ${key[0].upper() + key[1:]}
                            <ul>
                                % for item in value:
                                    % if key != "application":
                                    <li class="card-info"> ${item} </li>
                                    % else:
                                        <li class="card-info"> ${item}<ul>
                                        % for application_type, apps in value[item].iteritems():
                                            <li> ${application_type[0].upper() + application_type[1:]}
                                            <ul>
                                                % for app in apps:
                                                    <li>${app["name"]}</li>
                                                % endfor
                                            </ul>
                                            </li>
                                        % endfor
                                        </ul></li>
                                    % endif
                                % endfor
                            </ul>
                        </li>
                    % endif
                % endfor
            </ul>
          </li>
        </ul>
        %endfor
        </li>
     </ul>
     </div>
        </div>



        <div class="span4">
            <div class="acl-panel">
            <h4 class="acl-heading" id="selected-entity-heading"></h4>
            <div class="acl-description" id="json-view"></div>
            <div class="acl-management">
                <span style="padding-left:8px; font-size: large; font-weight:bold;">ACLs</span>
                <a><div class="acl-add-button pull-right pointer" onclick="newACL()"><i class="fa fa-plus create-acl"></i></div></a>
                <div class="acl-listing">
                     <table class="table table-striped">
                        <thead>
                          <tr>
                            <th>Role</th>
                            <th>Action</th>
                            <th>Operation</th>
                          </tr>
                        </thead>
                        <tbody id="acl-table-body">
                        </tbody>
                      </table>
                </div>
            </div>

            <div class="list-by-group">
                <br/>
                <h4>List privileges by group</h4>
                <input class="btn-list-by-group"></input>
                <div class="json-list-by-group" id="json-view"></div>
                <div>
            </div>
        </div>

        </div>
        % endif
    </div>
  </div>
</div>


<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/jstree.min.js"></script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery-jsonview/1.2.3/jquery.jsonview.min.js"></script>
<script>
  function entityClicked(entity, data){
      var parents = entity.parents;
      if(parents.length %2 == 1){
          return;
      }
      var treeStructString = "/" + entity.text.trim();
      for(var i = 0; i < parents.length-2; i ++){
          parentText = data.instance.get_node(parents[i]).text.trim();
          if (i %2 == 0){
              parentText = parentText[0].toLowerCase() + parentText.substring(1, parentText.length);
          }
          treeStructString = "/" + parentText + treeStructString;
      }
      $('.acl-heading').html(treeStructString.substring(1, treeStructString.length));
      refresfDetail(treeStructString);
  }

  function refresfDetail(treeStructString){

      var template = '<td> <a><i class="fa fa-pencil-square-o pointer" aria-hidden="true" onclick="editACL(this)"></i></a> ' +
            '<a><i class="fa fa-trash pointer" aria-hidden="true" onclick="delACL(this)" style="padding-left: 8px"></i></a> </td>';
      $.get("/cdap/details" + treeStructString, function(data){
          $("#acl-table-body").empty();
          $(".acl-description").JSONView(data,{ collapsed: true });
          privileges = data["privileges"];
          for(var role in privileges){
            $("#acl-table-body").append("<tr><td>"+ role + "</td><td>" + privileges[role]["actions"].join(",") + "</td>" + template + "<td></td></tr>");
          }
      })

      $.get("/cdap/list_roles_by_group" + treeStructString, function(data){
          $('.user-group').empty();
          for (var i=0; i < data.length; i++){
              var option = document.createElement("option");
              option.text = data[i]["name"];
              $('.user-group').append(option);
          }
      })
  }

  $('.btn-list-by-group').bind('input', function() {
      $.get("/cdap/list_privileges_by_group/" + $(this).val(), function(data){
          $(".json-list-by-group").JSONView(data);
      })
});

  function newACL() {
      $("#new-acl-popup").modal();
  };

  function delACL(element) {
      var tds = element.parentElement.parentElement.parentElement.children;
      var role = tds[0].textContent;
      var actions = tds[1].textContent.split(",");
      var path = $(".acl-heading").text();
      console.log(role);
      console.log(actions);

      // get data from backend
      $("body").css("cursor", "progress");
      $.ajax({
      type: "POST",
      url: "/cdap/revoke",
      data: {"role":role, "actions":actions, "path":path},
      success: function(){
            refresfDetail("/" + path);
            $("body").css("cursor", "default");
            },
        });
  }

  function editACL(element){
      newACL();
      var tds = element.parentElement.parentElement.parentElement.children;
      var role = tds[0].textContent;
      var actions = tds[1].textContent.split(",");
      // Set checkbox
      var checkboxes = $( "input:CHECKBOX" );
      for (var i = 0; i < checkboxes.length; i++){
          if (actions.indexOf(checkboxes[i].value) != -1){
              checkboxes[i].checked = true;
          }
      }
      // Set select pannel
      $(".user-group").val(role)
  }

  function delACL(element) {
      var tds = element.parentElement.parentElement.parentElement.children;
      var role = tds[0].textContent;
      var actions = tds[1].textContent.split(",");
      var path = $(".acl-heading").text();
      console.log(role);
      console.log(actions);
      $.ajax({
      type: "POST",
      url: "/cdap/revoke",
      data: {"role":role, "actions":actions, "path":path},
      success: function(){
            refresfDetail("/" + path);
            },
        });
  }

  function saveACL() {
      var allActions = ["READ","WRITE","EXECUTE","ADMIN","ALL"];
      var role = $(".user-group").find(":selected").text();
      var path = $(".acl-heading").text();
      var actions = [];
      var checked = $( "input:checked" )
      for(var i = 0; i < checked.length; i++ ){
          console.log(checked[i].value);
          checked[i].checked = false;
          actions.push(checked[i].value);
      }
      $("body").css("cursor", "progress");
      $.ajax({
      type: "POST",
      url: "/cdap/revoke",
      data: {"role":role, "actions":allActions, "path":path},
      success: function(){
              $.ajax({
              type: "POST",
              url: "/cdap/grant",
              data: {"role":role, "actions":actions, "path":path},
              success: function(){
                    refresfDetail("/" + path);
                    $("body").css("cursor", "default");
                    },
                });
            },
        });
  }

  function cdap_submit(){
      var username = $("#cdap_username").val();
      var password = $("#cdap_password").val();
      $.ajax({
      type: "POST",
      url: "/cdap/authenticate",
      data: {"username":username, "password":password},
      success: function(){
          window.location.reload();
            },
    });
  }

  $(document).ready(function(){
      if($(".is_authenticated").text()=="False"){
        $("#popup").modal();
      }

      $('#jstree').on('changed.jstree', function (e, data) {
        var r = data.instance.get_node(data.selected[data.selected.length-1])
        entityClicked(r, data);
  })

      // Temp: expand all
     // $('#jstree').on('loaded.jstree', function () {
    //   $('#jstree').jstree('open_all');
  //})

      $('#jstree').jstree(
            {"core" : {
    "animation" : 0,
    "check_callback" : true,
    "themes" : { "stripes" : true,        "theme": "default",
        "dots": true,
        "icons": true},

  },
  "types" : {
    "#" : {
      "max_children" : 1,
      "max_depth" : 4,
      "valid_children" : ["root"]
    },
    "root" : {
      "icon" : "/static/3.3.1/assets/images/tree_icon.png",
      "valid_children" : ["default"]
    },
    "default" : {
      "valid_children" : ["default"]
    },
    "file" : {
      "icon" : "glyphicon glyphicon-file",
      "valid_children" : []
    }
  },
  "plugins" : [
    "search", "types", "wholerow"
  ]
    });


  });
</script>

${commonfooter(request, messages) | n,unicode}