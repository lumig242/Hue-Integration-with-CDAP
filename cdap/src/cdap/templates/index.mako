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
                            <th>Authorization</th>
                            <th>Action</th>
                          </tr>
                        </thead>
                        <tbody id="acl-table-body">
                          <tr>
                            <td></td>
                            <td></td>
                            <td></td>
                          </tr>
                        </tbody>
                      </table>
                </div>
                <div class="acl-new">
                    <p class="acl-adding">
                        <div class="acl-adding-panel">
                            <a class="pointer pull-right" style="margin-right: 4px" onclick="closeACL()">
                                <i class="fa fa-times"></i>
                            </a>
                              <select name="user-group" class="user-group">
                                </select>
                                <br/>
                            <a class="pointer pull-right" style="margin-right: 4px" onclick="closeACL()">
                                <i class="fa fa-check"></i>
                            </a>
                                <label class="checkbox inline-block">
                                    <input type="checkbox" data-bind="checked: r">
                                    Read <span class="muted">(r)</span>
                                </label>
                                <label class="checkbox inline-block">
                                    <input type="checkbox" data-bind="checked: r">
                                    Write <span class="muted">(w)</span>
                                </label>
                                                                <label class="checkbox inline-block">
                                    <input type="checkbox" data-bind="checked: r">
                                    Execute <span class="muted">(x)</span>
                                </label>
                                            <label class="checkbox inline-block">
                                    <input type="checkbox" data-bind="checked: r">
                                    ADMIN <span class="muted">(admin)</span>
                                </label>
                                            <label class="checkbox inline-block">
                                    <input type="checkbox" data-bind="checked: r">
                                    All <span class="muted">(all)</span>
                                </label>
                        </div>
                    </p>

                </div>
            </div>

            <div class="list-by-group">
                <br/git ad>
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

      $.get("/cdap/details" + treeStructString, function(data){
          $("#acl-table-body").empty();
          $(".acl-description").JSONView(data,{ collapsed: true });
          privileges = data["privileges"];
          for(var i = 0; i < privileges.length; i++){
              var p = privileges[i];
              console.log(p);
            $("#acl-table-body").append("<tr><td>"+ p["role"] + "</td><td></td><td>" + p["actions"] + "</td></tr>");
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
      $('.acl-adding-panel').show();
      $('.acl-add-button').hide();
  };

  function closeACL() {
      $('.acl-adding-panel').hide();
      $('.acl-add-button').show();
  };

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
      $('#jstree').on('loaded.jstree', function () {
       $('#jstree').jstree('open_all');
  })

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