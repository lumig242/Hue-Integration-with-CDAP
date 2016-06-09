/* Global helper functions */
Array.prototype.unique = function () {
  return this.reduce(function (accum, current) {
    if (accum.indexOf(current) < 0) {
      accum.push(current);
    }
    return accum;
  }, []);
}

/* Authentication */
function cdap_submit() {
  var username = $("#cdap_username").val();
  var password = $("#cdap_password").val();
  $.ajax({
    type: "POST",
    url: "/cdap/authenticate",
    data: {"username": username, "password": password}
  }).done(function () {
      window.location.reload();
    }
  ).fail(function (data) {
    console.log(data);
    alert(data["responseText"]);
    window.location.reload();
  });
}

/* Tab switching */
$(".nav-role").on("click", function(){
  $(".role-management").show();
  $(".privilege-management").hide();
  $(".nav-privilege").removeClass('active');
  $(".nav-role").addClass('active');
  refreshRoleTable();
});

$(".nav-privilege").on("click", function(){
  $(".privilege-management").show();
  $(".role-management").hide();
  $(".nav-privilege").addClass('active');
  $(".nav-role").removeClass('active');
});


/* Related to privileges managements */
function entityClicked(entity, data) {
  var parents = entity.parents;
  if (parents.length % 2 == 1) {
    return;
  }
  var treeStructString = "/" + entity.text.trim();
  for (var i = 0; i < parents.length - 2; i++) {
    parentText = data.instance.get_node(parents[i]).text.trim();
    if (i % 2 == 0) {
      parentText = parentText[0].toLowerCase() + parentText.substring(1, parentText.length);
    }
    treeStructString = "/" + parentText + treeStructString;
  }
  $('.acl-heading').html(treeStructString.substring(1, treeStructString.length));
  refresfDetail(treeStructString);
}

function refresfDetail(treeStructString) {

  var template = '<td> <a><i class="fa fa-pencil-square-o pointer" aria-hidden="true" onclick="editACL(this)"></i></a> ' +
    '<a><i class="fa fa-trash pointer" aria-hidden="true" onclick="delACL(this)" style="padding-left: 8px"></i></a> </td>';
  $.get("/cdap/details" + treeStructString, function (data) {
    $("#acl-table-body").empty();
    $(".acl-description").JSONView(data, {collapsed: true});
    privileges = data["privileges"];
    for (var role in privileges) {
      $("#acl-table-body").append("<tr><td>" + role + "</td><td>" + privileges[role]["actions"].unique().join(",") + "</td>" + template + "<td></td></tr>");
    }
  })

  $.get("/cdap/list_roles_by_group" + treeStructString, function (data) {
    $('.user-group').empty();
    for (var i = 0; i < data.length; i++) {
      var option = document.createElement("option");
      option.text = data[i]["name"];
      $('.user-group').append(option);
    }
  })
}

$('.btn-list-by-group').bind('input', function () {
  $.get("/cdap/list_privileges_by_group/" + $(this).val(), function (data) {
    $(".json-list-by-group").JSONView(data);
  })
});


function newACL() {
  $("#new-acl-popup").modal();
  setPrivCheckbox();
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
    data: {"role": role, "actions": actions, "path": path},
    success: function (data) {
      refresfDetail("/" + path);
      $("body").css("cursor", "default");
      if (data.length > 0) {
        alert("Can not revoke some privileges as they are defined on upper layer entites at: " + data);
      }
    },
  });
}

function editACL(element) {
  newACL();
  var tds = element.parentElement.parentElement.parentElement.children;
  var role = tds[0].textContent;
  var actions = tds[1].textContent.split(",");
  // Set select pannel
  $(".user-group").val(role)
  // Set checkbox
  setPrivCheckbox();
}

function saveACL() {
  var allActions = ["READ", "WRITE", "EXECUTE", "ADMIN", "ALL"];
  var role = $(".user-group").find(":selected").text();
  var path = $(".acl-heading").text();
  var actions = [];
  var checked = $("input:checked");
  for (var i = 0; i < checked.length; i++) {
    console.log(checked[i].value);
    checked[i].checked = false;
    actions.push(checked[i].value);
  }
  $("body").css("cursor", "progress");
  $.ajax({
    type: "POST",
    url: "/cdap/revoke",
    data: {"role": role, "actions": allActions, "path": path},
    success: function () {
      $.ajax({
        type: "POST",
        url: "/cdap/grant",
        data: {"role": role, "actions": actions, "path": path},
        success: function () {
          refresfDetail("/" + path);
          $("body").css("cursor", "default");
        },
      });
    },
  });
}


function setPrivCheckbox() {
  var role = $(".user-group").find(":selected").text();
  var tr = $("td").filter(function () {
    return $(this).text() == role;
  }).closest("tr");
  if (tr.length > 0) {
    var actions = tr.children()[1].textContent.split(",");
  } else {
    var actions = [];
  }
  // Set checkbox
  var checkboxes = $("input:CHECKBOX");
  for (var i = 0; i < checkboxes.length; i++) {
    checkboxes[i].checked = false;
    if (actions.indexOf(checkboxes[i].value) != -1) {
      checkboxes[i].checked = true;
    }
  }
}


/* Role management */
function getGroupMultiSelector(role) {
  $.get("/cdap/list_all_groups", function(groups){
    var select = '<select class="group-selector" data-placeholder="None..." style="width:350px;" multiple>';
    groups.forEach(function(group){
      select += $('<option></option>').val(group).html(group);
    });
    select += "</select>";
  });
}


function refreshRoleTable() {
  $(".list-role-table").bootstrapTable('destroy');
  $.get("/cdap/list_roles_by_group", function(data){
    var dataField = [];
    data.forEach(function(item){
      dataField.push({
        state : false,
        role: item.name,
        group: item.groups.join(","),
      });
    });
    $(".list-role-table").bootstrapTable({
    columns: [{
               field: 'state',
                checkbox: true,
                align: 'center',
    }, {
        field: 'role',
        title: 'Name'
    }, {
        field: 'group',
        title: 'Group'
    }],
    data: dataField
    });
  });
}

function deleteRole() {
  var selections = $(".list-role-table").bootstrapTable('getAllSelections');
  selections.forEach(function(item){
    $.get("/cdap/drop_role/" + item.role, function(){
      $(".list-role-table").bootstrapTable('remove', {field:"role", values:[item.role]})
    });
  });
}

function saveRole() {
  $.get("/cdap/create_role/" + $("#new-rolename").val(), function(){
    $(".list-role-table").bootstrapTable('destroy');
    refreshRoleTable();
  });
}

function updateRoleACL(role) {
  $('.selected-role').html(role);
  var template = '<td><a><i class="fa fa-trash pointer" aria-hidden="true" onclick="deletePrivilegeByRole(this)" style="padding-left: 8px"></i></a> </td>';
  $("#role-acl-table-body").empty();
  $.get("/cdap/list_privileges_by_role/" + role, function (data) {
    data.forEach(function(privilege){
        $("#role-acl-table-body").append("<tr><td>" + privilege.authorizables.split("/").slice(3).join("/") + "</td><td>"
        + privilege.actions + "</td>" + template + "<td></td></tr>");

    });
  });
}

function deletePrivilegeByRole(element){
  var tr = element.parentElement.parentElement.parentElement;
  var path = tr.children[0].textContent;
  var action = tr.children[1].textContent;
  var role = $('.selected-role').text();
  $("body").css("cursor", "progress");
  $.ajax({
    type: "POST",
    url: "/cdap/revoke",
    data: {"role": role, "actions": [action], "path": path},
    success: function (data) {
      tr.remove();
      $("body").css("cursor", "default");
    },
  });
}


function editRole() {
  $(".group-selector").empty();
  $(".group-selector").trigger("chosen:updated");

  var selections = $(".list-role-table").bootstrapTable('getAllSelections');
  if(selections.length == 0)  return;

  var item = selections[0];
  var affGroups = item.group.split(",");
  $("#edit-role-modal-title").html(item.role);
  $.get("/cdap/list_all_groups", function(groups){
    groups.forEach(function(group){
      if(affGroups.indexOf(group) == -1){
        var option = $('<option></option>').val(group).html(group);
      }else{
        var option = $('<option selected></option>').val(group).html(group);
      }
      $(".group-selector").append(option);
    });

    $('#edit-role-popup').on('shown.bs.modal', function () {
      $(".group-selector").trigger("chosen:updated");
      $(".group-selector").chosen();
    });
    $('#edit-role-popup').modal();
  });
}


function saveEditedRole() {
  role = $("#edit-role-modal-title").text();
  var options = $(".group-selector")[0].options;
  var selected = [];
  for(var i = 0; i < options.length; i++){
    if(options[i].selected){
      console.log(options[i].text);
      selected.push(options[i].text);
    }
  }
  $.ajax({
    type: "POST",
    url: "/cdap/alter_role_by_group",
    data: {"role": role, "groups": selected},
  }).done(function () {
    refreshRoleTable();
    }
  ).fail(function (data) {
  });
}