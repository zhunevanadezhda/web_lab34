const ToDos = {

    loadingElement: document.getElementById('loading'),
    sectionContainer: document.getElementById('section-container'),
    errorElement: document.getElementById('error'),
    todoList: document.getElementById('todo-list'),

    async init() {
        try {
            const todos = await this.fetchTodos();
            this.fillTodosList(todos);
        } catch (e) {
            this.showError(e.message)
            return;
        }
    },

    setLoading(loading) {
        this.loadingElement.style.display = loading ? '' : 'none';
    },

    showError(error) {
        this.errorElement.textContent = error;
        this.errorElement.style.display = '';
    },

    async fetchTasks() {
        this.setLoading(true);
        const tasksResponse = await fetch(`${window.origin}/getTasks`);
        this.setLoading(false);
        if (!tasksResponse.ok) {
            throw new Error('Не удалось получить задачи. ');
        }
        const tasks = await tasksResponse.json();
        return tasks;
    },

    async fetchTodos() {
        this.setLoading(true);
        const todosResponse = await fetch('https://jsonplaceholder.typicode.com/todos');
        this.setLoading(false);
        if (!todosResponse.ok) {
            throw new Error('Не удалось получить комментарии. ');
        }
        const todos = await todosResponse.json();
        return todos;
    },

    async fillTodosList(todos) {
        for (const todo of todos) {
            const todoItem = document.querySelector(`li[data-id="${todo.id}"]`)
            let task_status = 0
            let task_description = 0
            if(todoItem)
            {
                const tasks = await this.fetchTasks();
                for (let i = 0; i < tasks.length; i++) {
                    if(tasks[i].id === todo.id) {
                        task_status = tasks[i].completed;
                        task_description = tasks[i].description;
                        break;
                    }
                }
                // List Item (ToDo)
                const headerBlock = document.getElementById('header-block'+todo.id);
                // Task checkbox
                const checkboxDiv = document.createElement('div');
                checkboxDiv.classList.add("checkbox-completed");
                checkboxDiv.classList.add("float-right");
                checkboxDiv.classList.add("custom-control");
                checkboxDiv.classList.add("custom-checkbox");
                checkboxDiv.classList.add("form-control-lg");
                const chk = document.createElement('input');
                chk.setAttribute('type',"checkbox");
                chk.setAttribute('name',"taskComplete");
                chk.classList.add("custom-control-input");
                chk.setAttribute('id',"customCheck"+todo.id);
                const button_cha = document.createElement('button'); // Change button
                button_cha.classList.add('btn');
                button_cha.classList.add('btn-outline-success');
                button_cha.classList.add('btn-sm');
                //button_cha.classList.add('btn-remove-todo')
                button_cha.classList.add('ml-auto');
                button_cha.textContent = 'Изменить';
                button_cha.addEventListener('click', () => { this.changeTodo(todo.id) });
                const chkLabel = document.createElement('label');
                chkLabel.htmlFor = "customCheck"+todo.id;
                if(task_status === 0)
                {
                    chk.checked = false;
                    todoItem.appendChild(button_cha);
                    chkLabel.textContent = 'Выполнить';
                }
                else {
                    chk.checked = true;
                    todoItem.classList.add("completed-todo");
                    headerBlock.classList.add("completed-todo");
                    chkLabel.textContent = 'Сделано';
                }
                chk.addEventListener('change', async () => {
                    let currentCheckboxStatus = chk.checked
                    if (!confirm('Вы уверены, что хотите поменять статус этого задания?')) {
                        if (currentCheckboxStatus)
                            chk.checked = false
                        else
                            chk.checked = true
                        return;
                    }
                    let entry = {};
                    if(chk.checked)
                    {
                        todoItem.classList.add("completed-todo");
                        headerBlock.classList.add("completed-todo");
                        entry = {
                            task_id: todo.id,
                            action: "completed"
                        };
                        chkLabel.textContent = 'Сделано';
                        todoItem.removeChild(button_cha);
                    }
                    else {
                        todoItem.classList.remove("completed-todo");
                        headerBlock.classList.remove("completed-todo");
                        entry = {
                            task_id: todo.id,
                            action: "uncompleted"
                        };
                        chkLabel.textContent = 'Выполнить';
                        todoItem.appendChild(button_cha);
                    }
                    await fetch(`${window.origin}`, {
                            method: "PATCH",
                            credentials: "include",
                            body: JSON.stringify(entry),
                            cache: "no-cache",
                            headers: new Headers({
                                "content-type": "application/json"
                            })
                        });
                });
                checkboxDiv.appendChild(chk);
                checkboxDiv.appendChild(chkLabel);
                todoItem.appendChild(checkboxDiv);
                const divDesc = document.createElement('div');
                divDesc.classList.add("description-block");
                divDesc.appendChild(document.createTextNode(task_description))
                todoItem.appendChild(divDesc)
                todoItem.appendChild(document.createElement('hr'));

                // Todo comment
                const titleEl = document.createElement('div');
                const header2 = document.createElement('h2');
                const comment = document.createElement('div');
                header2.textContent = "Комментарий к задаче:";
                titleEl.appendChild(header2);
                comment.textContent = todo.title;
                titleEl.appendChild(comment);
                titleEl.classList.add('collapse');
                titleEl.setAttribute('id', "demo"+todo.id);
                todoItem.appendChild(titleEl);
                todoItem.appendChild(document.createElement('br'));
                // Remove button
                const button_rem = document.createElement('button');
                button_rem.classList.add('btn');
                button_rem.classList.add('btn-outline-danger');
                button_rem.classList.add('btn-lg');
                //button_rem.classList.add('btn-remove-todo')
                button_rem.classList.add('ml-auto');
                button_rem.textContent = 'Удалить';
                button_rem.addEventListener('click', () => { this.removeTodo(todo.id) });
                todoItem.appendChild(button_rem);
                if(task_status === 0)
                {
                    todoItem.appendChild(button_cha);
                }
                // Add todo to list
                this.todoList.appendChild(todoItem);
            }
        }
    },

    async changeTodo(id) {
        if (!confirm('Вы уверены, что хотите изменить это задание?')) {
            return;
        }
        try{
            this.setLoading(true);
            const reply = await fetch(`${window.origin}/change/${id}`);
            this.setLoading(false);
            if (!reply.ok) {
                throw new Error("Не удалось получить данные задачи.");
            }
            const data = await reply.json();

            var newModal = `
                <div class="modal fade" id="edit-todo-window${id}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
                   <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="title-modal${id}">Редактирование задачи</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                        </div>
                        <div class="modal-body">
                            <form>
                                <div class="form-group">
                                <label class="col-form-label">Название задачи:</label>
                                <input type="text" class="form-control" id='edit-name${id}'>
                                </div>
                                <div class="form-group">
                                <label class="col-form-label">Описание задачи:</label>
                                <input type="text" class="form-control" id='edit-description${id}'>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                        <button type="button" class="btn btn-dark" data-dismiss="modal">Закрыть</button>
                        <button type="button" class="btn btn-success" id='save-todo-edit${id}'>Сохранить изменения</button>
                        </div>
                    </div>
                    </div>
                </div>
            `;
            $('body').append(newModal);
            $('#edit-todo-window'+id).modal('show');
            $('#edit-name'+id).val(data['name']);
            $('#edit-description'+id).val(data['description']);
            $('#save-todo-edit'+id).on('click', async () => {
            let new_name=$('#edit-name'+id).val()
            let new_description=$('#edit-description'+id).val()
            if (new_name==data['name'] && new_description==data['description']) {$('#edit-todo-window'+id).modal('hide'); return}
            else{
                const entry = {
                        task_id: id,
                        task_name: new_name,
                        task_description: new_description
                    };

                await fetch(`${window.origin}`, {
                    method: "PATCH",
                    credentials: "include",
                    body: JSON.stringify(entry),
                    cache: "no-cache",
                    headers: new Headers({
                        "content-type": "application/json"
                    })
                });
                $('#edit-todo-window'+id).modal('hide');
                $('[data-target="#demo'+id+'"]')[0].innerText=new_name;//this.init();
            }});
        }
        catch (error) {
            this.showError(error.message);
        }
    },

    async removeTodo(id) {
        if (!confirm('Вы уверены, что хотите удалить это задание?')) {
            return;
        }

        try {
            this.setLoading(true);
            const res = await fetch(`https://jsonplaceholder.typicode.com/todos/${id}`, { method: 'delete' });
            this.setLoading(false);
            if (!res.ok) {
                throw new Error("Не удалось удалить запись.");
            }

            const entry = {
                task_id: id
            };

            await fetch(`${window.origin}`, {
                method: "DELETE",
                credentials: "include",
                body: JSON.stringify(entry),
                cache: "no-cache",
                headers: new Headers({
                    "content-type": "application/json"
                })
            });
            document.querySelector(`li[data-id="${id}"]`).remove();
        }
        catch (error) {
            this.showError(error.message);
        }
    },
}

ToDos.init();