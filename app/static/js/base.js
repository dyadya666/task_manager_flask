// CRUD for "Project"
// Create project
$(function () {
    $('#add_project').on('click', function () {
        var name = $('#new_project').val();
        if (name.trim().length == 0){
            document.getElementById('info').innerHTML = 'Cannot be blank!';
            $('#info').show();
            return;
        } else {
            $('#info').hide();
        }

        $.post("/create_project", {
                name: name
        }).done(function (result) {
            if (result['result'] === true){
                $('#info').show();
                location.reload();
            } else if (result['result'] === false){
                alert('Project was not created!');
            }
        }).fail(function () {
            alert('Server error!');
        });
    });
});

// Delete Project
function deleteProject(project_id) {
        $.post("/delete_project", {
            project_id: project_id
        }).done(function (result) {
            if (result['result'] === true){
                $('#info').show();
                location.reload();
            } else if (result['result'] === false){
                alert('Project was not deleted!');
            }
        }).fail(function () {
            alert('Server error!');
        });
}

//Update Project
function editProject(project_id, project_name) {
    $('#name_' + project_name).hide();
    $('#project_name' + project_id).show();
    $('#edit' + project_id).hide();
    $('#save' + project_id).show();
}

function updateProject(project_id, project_name) {
    var new_name = $('#project_name' + project_id).val();
    if (new_name.trim().length == 0){
        document.getElementById('name_' + project_name).innerHTML = 'Cannot be blank!';
        $('#name_' + project_name).show();
        return;
    } else {
        $('#name_' + project_name).hide();
    }

    $.post('/update_project', {
        project_id: project_id,
        new_name: new_name
    }).done(function (result) {
        if (result['result'] === true){
            location.reload();
        } else if (result['result'] === false){
            alert('Project was not updated!');
        }
    }).fail(function () {
        alert('Server error!');
    });
}

//Create Task
$(function () {
    $('#add_task').on('click', function () {
        var new_name = $('#new_task').val();
        var project_id = $('#project_id').val();
        if (new_name.trim().length == 0){
            document.getElementById('task_info').innerHTML = 'Cannot be blank!';
            $('#task_info').show();
            return;
        } else {
            $('#task_info').hide();
        }
        $.post("/create_task", {
            new_name: new_name,
            project_id: project_id
        }).done(function (result) {
            if (result['result'] === true){
                location.reload();
            } else if (result['result'] === false){
                alert('Task was not created!');
            }
        }).fail(function () {
            alert('Server error!');
        });
    });
});

//Delete Task
function deleteTask(task_id, project_id) {
    $.post("/delete_task", {
        task_id: task_id,
        project_id: project_id
    }).done(function (result) {
        if (result['result'] == true){
            location.reload();
        } else if (result['result'] == false){
            alert('Task was not deleted!');
        }
    }).fail(function () {
        alert('Server error!');
    })
}

//Update Task
function editTask(task_id) {
    $('#task_name' + task_id).hide();
    $('#new_task_name' + task_id).show();
    $('#edit_task' + task_id).hide();
    $('#save_task' + task_id).show();
}


function updateTask(task_id, project_id) {
    var new_name = $('#new_task_name' + task_id).val();
    if (new_name.trim().length == 0){
        document.getElementById('new_task_info').innerHTML = 'Cannot be blank!';
        $('#new_task_info').show();
        return;
    } else {
        $('#new_task_info').hide();
    }

    $.post("/update_task", {
        task_id: task_id,
        project_id: project_id,
        new_name: new_name
    }).done(function (result) {
        if (result['result'] == true){
            location.reload();
        } else if (result['result'] == false){
            alert('Task was not updated!');
        }
    }).fail(function () {
        alert('Server error!');
    });
}
