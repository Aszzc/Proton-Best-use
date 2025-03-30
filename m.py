import os
import glob
import configparser

def parse_wireguard_config(file_path):
    """解析单个WireGuard配置文件"""
    config = configparser.ConfigParser()
    # 禁用小写转换
    config.optionxform = str
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # WireGuard配置文件需要特殊处理，因为它使用[Section]标记
    # 我们需要将内容转换为configparser能识别的格式
    sections = []
    current_section = None
    current_lines = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('[') and line.endswith(']'):
            if current_section and current_lines:
                sections.append((current_section, current_lines))
            current_section = line[1:-1]  # 移除方括号
            current_lines = []
        elif current_section and '=' in line:
            current_lines.append(line)
    
    if current_section and current_lines:
        sections.append((current_section, current_lines))
    
    # 将解析的内容添加到config对象
    for section_name, lines in sections:
        config[section_name] = {}
        for line in lines:
            key, value = line.split('=', 1)
            config[section_name][key.strip()] = value.strip()
    
    return config

def merge_wireguard_configs(input_dir, output_file):
    """合并WireGuard配置文件"""
    config_files = glob.glob(os.path.join(input_dir, "*.conf"))
    
    if not config_files:
        print("未找到任何WireGuard配置文件！")
        return
    
    # 存储合并后的配置
    merged_config = configparser.ConfigParser()
    merged_config.optionxform = str
    peer_count = 0
    
    for i, config_file in enumerate(config_files):
        config = parse_wireguard_config(config_file)
        
        # 只使用第一个文件的Interface部分
        if i == 0 and 'Interface' in config:
            merged_config['Interface'] = config['Interface']
        
        # 添加所有的Peer部分
        if 'Peer' in config:
            peer_count += 1
            merged_config[f'Peer{peer_count}'] = config['Peer']
    
    # 写入合并后的配置文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入Interface部分
        if 'Interface' in merged_config:
            f.write('[Interface]\n')
            for key, value in merged_config['Interface'].items():
                f.write(f'{key} = {value}\n')
            f.write('\n')
        
        # 写入所有Peer部分
        for section in merged_config.sections():
            if section.startswith('Peer'):
                f.write('[Peer]\n')
                for key, value in merged_config[section].items():
                    f.write(f'{key} = {value}\n')
                f.write('\n')
    
    print(f"已成功合并 {len(config_files)} 个配置文件到 {output_file}")
    print(f"包含 1 个 Interface 和 {peer_count} 个 Peer 配置")

# 使用示例
if __name__ == "__main__":
    input_directory = "configs"  # 修改为你的配置目录
    output_filename = "merged_wg.conf"        # 修改为输出文件名
    
    merge_wireguard_configs(input_directory, output_filename)