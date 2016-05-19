<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Cdap", "cdap", user) | n,unicode}
${shared.menubar(section='mytab')}



## Use double hashes for a mako template comment
## Main body

<div class="container-fluid">
  <div class="card">
    <h2 class="card-heading simple">Namespaces</h2>
    <div class="card-body">
      <div class="panel-group" id="accordion">
        % for index, row in enumerate(namespaces):
            <div class="panel panel-default card-heading" id="panel-${index}">
                <div class="panel-heading">
                    <h4 class="panel-title">
                        <a data-toggle="collapse" data-target="#collapse-${index}" href="#collapse-${index}">
                            Namespaces: ${row['name']}
                        </a>
                    </h4>
                </div>
                <div id="collapse-${index}" class="panel-collapse collapse">
                    % for k,v in row.items():
                        <div class="card-info">${k} : ${v}</div>
                    % endfor
                </div>
            </div>
          % endfor
      </div>
    </div>
  </div>
</div>
${commonfooter(request, messages) | n,unicode}