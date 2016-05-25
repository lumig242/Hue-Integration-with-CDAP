<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("cdap", "cdap", user) | n,unicode}
${shared.menubar(section='mytab')}

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/themes/default/style.min.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-jsonview/1.2.3/jquery.jsonview.css">

<style>
    .acl-heading {
        margin-top: 0px;
        padding-top: 0px;
        word-wrap: break-word;
    }

    #jstree {
        margin-top:5px;
    }

    .row-fluid .span8 {
        width : 48%;
        height: 100%;
    }

    .row-fluid .span4 {
        width: 48%;
        height: 100%;
    }

    #json-view{
        width:600px;
    }

    .jsonview ul li{
        line-height: 15px;
    }

    .acl-panel{
        border-left: 1px solid #e5e5e5;
        padding-top: 6px;
        padding-left: 18px;
        height: 1000px;
    }

    .acl-adding-panel{
        display: none;
        width: 50%;
    }

</style>

## Use double hashes for a mako template comment
## Main body

<div class="container-fluid">
  <div class="card">
    <h2 class="card-heading simple">Entities</h2>
    <div class="card-body">
        <div class="row-fluid">

            <div class="span8">
            <div id="jstree">
     <ul>
        <li> Namespaces
        % for name, namespace in entities.items():
        <ul>
          <li>${name}
            <ul>
                % for key, value in namespace.items():
                    % if value:
                        <li> ${key[0].upper() + key[1:]}
                            <ul>
                                % for item in value:
                                    % if key != "application":
                                    <li class="card-info"> ${item} </li>
                                    % else:
                                        <li class="card-info"> ${item}<ul>
                                        % for application_type, apps in value[item].items():
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
                <h4>ACLs</h4>
                <div class="acl-listing"></div>
                <div class="acl-new">
                    <p class="acl-adding">
                        <div class="acl-adding-panel">
                            <a class="pointer pull-right" style="margin-right: 4px" onclick="closeACL()">
                                <i class="fa fa-times"></i>
                            </a>
                              <select name="user-group">
                                <option value="group1">group1</option>
                                <option value="group2">group2</option>
                                <option value="group3">group3</option>
                                <option value="group4">group4</option>
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
                        </div>
                    </p>
                    <div class="acl-add-button" onclick="newACL()"><i class="fa fa-plus create-acl"></i></div>
                </div>
            </div>
            </div>
        </div>

        </div>
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
          $(".acl-description").JSONView(data,{ collapsed: true });
      })
  }

  function newACL() {
      $('.acl-adding-panel').show();
      $('.acl-add-button').hide();
  };

  function closeACL() {
      $('.acl-adding-panel').hide();
      $('.acl-add-button').show();
  };

  $(document).ready(function(){
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