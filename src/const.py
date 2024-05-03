html=r'''<!DOCTYPE html>
<html lang="zh-cn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>渠道服账号</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="mt-5 mb-3">渠道服账号</h1>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th scope="col">选择</th>
                    <th scope="col">UUID</th>
                    <th scope="col">名称</th>
                    <th scope="col">操作</th>
                </tr>
            </thead>
            <tbody id="channelTableBody">
                <!-- 账号记录将在这里显示 -->
            </tbody>
        </table>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function renameChannel(uuid) {
            var newName = prompt("请输入新的账号名称");
            if (newName) {
                fetch(`/_idv-login/rename?uuid=${uuid}&new_name=${newName}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('账号已成功改名');
                            location.reload();
                        } else {
                            alert('改名失败');
                        }
                    });
            }
        }

        function deleteChannel(uuid) {
            var confirmDelete = confirm("确定要删除这个账号吗？");
            if (confirmDelete) {
                fetch(`/_idv-login/del?uuid=${uuid}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('账号已成功删除');
                            location.reload();
                        } else {
                            alert('删除失败');
                        }
                    });
            }
        }
        function switchChannel(uuid) {
            fetch(`/_idv-login/switch?uuid=${uuid}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.current==uuid) {
                            alert('模拟登录成功');
                            location.reload();
                        } else {
                            alert('写登录失败失败');
                        }
                    });
        }

        // 在页面加载时获取账号列表
        window.onload = function() {
            fetch('/_idv-login/list')
                .then(response => response.json())
                .then(data => {
                    var tableBody = document.getElementById('channelTableBody');
                    data.forEach(channel => {
                        var row = tableBody.insertRow();
                        row.insertCell().innerHTML = `<input type="checkbox" value="${channel.uuid}">`;
                        row.insertCell().innerHTML = channel.uuid;
                        row.insertCell().innerHTML = channel.name;
                        var actionsCell = row.insertCell();
                        actionsCell.innerHTML = `
                            <button onclick="switchChannel('${channel.uuid}')">登录</button>
                            <button onclick="renameChannel('${channel.uuid}')">改名</button>
                            <button onclick="deleteChannel('${channel.uuid}')">删除</button>
                        `;
                    });
                });
        }
    </script>
</body>
</html>'''