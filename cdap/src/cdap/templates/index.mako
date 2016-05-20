<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Cdap", "cdap", user) | n,unicode}
${shared.menubar(section='mytab')}

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/themes/default/style.min.css" />

## Use double hashes for a mako template comment
## Main body

<div class="container-fluid">
  <div class="card">
    <h2 class="card-heading simple">Entities</h2>
    <div class="card-body">
     <div id="jstree">
     <ul>
        <li> Namespaces
        % for name, namespace in entities.items():
        <ul>
          <li> Namespaces: ${name}
            <ul>
                % if namespace["streams"]:
                <li> Streams
                    <ul>
                        % for stream in namespace["streams"]:
                            <li class-"card-info"> ${stream} </li>
                        % endfor
                    </ul>
                </li>
                % endif

                % if namespace["datasets"]:
                <li> Datasets
                    <ul>
                        % for dataset in namespace["datasets"]:
                            <li class-"card-info"> ${dataset} </li>
                        % endfor
                    </ul>
                </li>
                % endif
            </ul>
          </li>
        </ul>
        %endfor
        </li>
     </ul>
     </div>

    <br/> <br/> <br/> <br/>

    </div>
  </div>
</div>


<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/jstree.min.js"></script>
<script>
  $(document).ready(function(){
    $('#jstree').jstree({
          "core" : {
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