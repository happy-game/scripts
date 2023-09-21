#!/bin/bash
# 用于复制公钥到目标服务器并开启密钥登陆
# 检查命令行参数数量
if [ "$#" -ne 3 ]; then
  echo "用法：$0 <USERNAME> <SERVER> <file>"
  exit 1
fi

# 从命令行参数获取USERNAME和SERVER
USERNAME="$1"
SERVER="$2"
FILE="$3"

# 复制公钥到目标服务器
echo "复制公钥到目标服务器..."
ssh-copy-id -i ~/.ssh/$FILE $USERNAME@$SERVER 

# 设置服务器密钥权限
echo "设置服务器密钥权限..."
ssh -t $USERNAME@$SERVER "chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys"

# 修改服务器SSH配置
echo "修改服务器SSH配置..."
ssh -t $USERNAME@$SERVER "sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config"
# 如果你希望禁用密码登录，可以取消下面这行的注释
# ssh -t $USERNAME@$SERVER "sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config"

# 重启服务器SSH服务
echo "重启服务器SSH服务..."
# 对于使用Systemd的系统（如Ubuntu 16.04+，CentOS 7+）：
ssh -t $USERNAME@$SERVER "sudo systemctl restart sshd"
# 对于使用SysV Init的系统（如Ubuntu 14.04，CentOS 6）：
# ssh -t $USERNAME@$SERVER "sudo service ssh restart"

echo "完成！现在你应该可以使用私钥登录到目标服务器了。"