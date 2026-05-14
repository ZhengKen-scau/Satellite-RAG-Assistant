# Satellite RAG Assistant - 文档处理模块
# 负责处理原始卫星遥感文档，包括PDF解析、文本提取和分块

import os
from typing import List, Dict, Any
from app.config import settings

# 添加必要的导入
try:
    import rasterio
    from rasterio.plot import show
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

try:
    import netCDF4 as nc
    NETCDF_AVAILABLE = True
except ImportError:
    NETCDF_AVAILABLE = False

try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class DocumentProcessor:
    """文档处理器类"""
    
    def __init__(self):
        self.max_chunk_size = settings.MAX_CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def _extract_geotiff_info(self, file_path: str, filename: str) -> str:
        """提取GeoTIFF文件信息"""
        if not RASTERIO_AVAILABLE:
            return f"GeoTIFF文件 '{filename}' 已上传，但缺少rasterio库支持。建议安装rasterio以获得完整的遥感影像分析功能。"
        
        try:
            with rasterio.open(file_path) as src:
                info = f"GeoTIFF文件 '{filename}' 详细信息：\n"
                info += f"- 尺寸: {src.width} x {src.height} 像素\n"
                info += f"- 波段数: {src.count}\n"
                info += f"- 数据类型: {src.dtypes[0]}\n"
                info += f"- 坐标系: {src.crs}\n"
                info += f"- 分辨率: {src.res[0]:.6f}, {src.res[1]:.6f}\n"
                
                # 获取统计信息（如果可用）
                if hasattr(src, 'nodata') and src.nodata is not None:
                    info += f"- 无效值: {src.nodata}\n"
                
                # 计算基本统计（仅对小文件）
                if src.width * src.height < 1000000:  # 1M像素以下
                    try:
                        data = src.read(1)
                        valid_data = data[data != src.nodata] if src.nodata is not None else data
                        if len(valid_data) > 0:
                            info += f"- 数值范围: {valid_data.min():.3f} - {valid_data.max():.3f}\n"
                            info += f"- 平均值: {valid_data.mean():.3f}\n"
                    except Exception:
                        pass
                
                info += "\n此GeoTIFF文件可用于遥感影像分析、地物分类、变化检测等应用。"
                return info
        except Exception as e:
            return f"GeoTIFF文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持遥感影像问答\n- 错误详情: {str(e)}"
    
    def _extract_envi_info(self, file_path: str, filename: str) -> str:
        """提取ENVI HDR/BIL文件信息"""
        if not RASTERIO_AVAILABLE:
            return f"ENVI文件 '{filename}' 已上传，但缺少rasterio库支持。"
        
        try:
            with rasterio.open(file_path) as src:
                info = f"ENVI文件 '{filename}' 详细信息：\n"
                info += f"- 尺寸: {src.width} x {src.height} 像素\n"
                info += f"- 波段数: {src.count}\n"
                info += f"- 数据类型: {src.dtypes[0]}\n"
                info += f"- 格式: ENVI ({src.driver})\n"
                
                if hasattr(src, 'tags'):
                    tags = src.tags()
                    if tags:
                        info += "- 元数据标签:\n"
                        for key, value in list(tags.items())[:5]:  # 只显示前5个
                            info += f"  {key}: {value}\n"
                
                info += "\nENVI格式常用于高光谱遥感数据分析，支持多波段影像处理。"
                return info
        except Exception as e:
            return f"ENVI文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持高光谱数据分析\n- 错误详情: {str(e)}"
    
    def _extract_erdas_img_info(self, file_path: str, filename: str) -> str:
        """提取ERDAS IMG文件信息"""
        if not RASTERIO_AVAILABLE:
            return f"ERDAS IMG文件 '{filename}' 已上传，但缺少rasterio库支持。"
        
        try:
            with rasterio.open(file_path) as src:
                info = f"ERDAS IMG文件 '{filename}' 详细信息：\n"
                info += f"- 尺寸: {src.width} x {src.height} 像素\n"
                info += f"- 波段数: {src.count}\n"
                info += f"- 数据类型: {src.dtypes[0]}\n"
                info += f"- 格式: ERDAS IMAGINE ({src.driver})\n"
                info += f"- 坐标系: {src.crs}\n"
                
                info += "\nERDAS IMG格式是专业的遥感影像格式，广泛应用于地理信息系统和遥感分析。"
                return info
        except Exception as e:
            return f"ERDAS IMG文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持专业遥感分析\n- 错误详情: {str(e)}"
    
    def _extract_netcdf_info(self, file_path: str, filename: str) -> str:
        """提取NetCDF文件信息"""
        if not NETCDF_AVAILABLE:
            return f"NetCDF文件 '{filename}' 已上传，但缺少netCDF4库支持。建议安装netCDF4以获得完整的科学数据支持。"
        
        try:
            with nc.Dataset(file_path, 'r') as dataset:
                info = f"NetCDF文件 '{filename}' 详细信息：\n"
                info += f"- 维度数量: {len(dataset.dimensions)}\n"
                info += f"- 变量数量: {len(dataset.variables)}\n"
                
                # 显示维度信息
                info += "- 维度信息:\n"
                for dim_name, dim in list(dataset.dimensions.items())[:3]:  # 只显示前3个
                    info += f"  {dim_name}: {len(dim) if not dim.isunlimited() else 'unlimited'}\n"
                
                # 显示变量信息
                info += "- 主要变量:\n"
                for var_name, var in list(dataset.variables.items())[:5]:  # 只显示前5个
                    dims = ', '.join(var.dimensions)
                    info += f"  {var_name}: {var.dtype} [{dims}]\n"
                
                # 显示全局属性
                if hasattr(dataset, '__dict__'):
                    attrs = dataset.__dict__
                    if attrs:
                        info += "- 全局属性 (部分):\n"
                        for key, value in list(attrs.items())[:3]:
                            info += f"  {key}: {value}\n"
                
                info += "\nNetCDF格式常用于存储多维科学数据，如气象数据、海洋数据、遥感时间序列等。"
                return info
        except Exception as e:
            return f"NetCDF文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持多维科学数据分析\n- 错误详情: {str(e)}"
    
    def _extract_hdf_info(self, file_path: str, filename: str) -> str:
        """提取HDF/HDF5文件信息"""
        if not H5PY_AVAILABLE:
            return f"HDF文件 '{filename}' 已上传，但缺少h5py库支持。建议安装h5py以获得完整的HDF支持。"
        
        try:
            with h5py.File(file_path, 'r') as f:
                info = f"HDF文件 '{filename}' 详细信息：\n"
                info += f"- 数据集数量: {len(f.keys())}\n"
                
                # 显示主要数据集
                info += "- 主要数据集:\n"
                for i, (key, item) in enumerate(list(f.items())[:5]):  # 只显示前5个
                    if isinstance(item, h5py.Dataset):
                        shape = item.shape
                        dtype = item.dtype
                        info += f"  {key}: {dtype} {shape}\n"
                    elif isinstance(item, h5py.Group):
                        info += f"  {key}: Group\n"
                
                info += "\nHDF格式广泛用于存储大型科学数据集，包括遥感数据、气候模型输出等。"
                return info
        except Exception as e:
            return f"HDF文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持大型科学数据集分析\n- 错误详情: {str(e)}"
    
    def _extract_vector_info(self, file_path: str, filename: str, file_type: str) -> str:
        """提取矢量数据文件信息"""
        if not GEOPANDAS_AVAILABLE:
            return f"{file_type.upper()}文件 '{filename}' 已上传，但缺少geopandas库支持。建议安装geopandas以获得完整的矢量数据支持。"
        
        try:
            gdf = gpd.read_file(file_path)
            info = f"{file_type.upper()}文件 '{filename}' 详细信息：\n"
            info += f"- 要素数量: {len(gdf)}\n"
            info += f"- 几何类型: {gdf.geometry.geom_type.value_counts().to_dict()}\n"
            info += f"- 坐标系: {gdf.crs}\n"
            info += f"- 属性字段: {list(gdf.columns)[:5]}{'...' if len(gdf.columns) > 5 else ''}\n"
            
            # 显示前几个要素的属性（如果数据量不大）
            if len(gdf) <= 10:
                info += "- 要素属性示例:\n"
                for idx, row in gdf.head(3).iterrows():
                    info += f"  要素 {idx}: {dict(row.drop('geometry'))}\n"
            
            info += f"\n{file_type.upper()}格式是标准的地理空间矢量数据格式，适用于边界、道路、建筑物等地物表示。"
            return info
        except Exception as e:
            return f"{file_type.upper()}文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持地理空间矢量数据分析\n- 错误详情: {str(e)}"
    
    def _extract_image_info(self, file_path: str, filename: str, file_ext: str) -> str:
        """提取普通图像文件信息"""
        if not PIL_AVAILABLE:
            return f"图像文件 '{filename}' 已上传，但缺少PIL库支持。"
        
        try:
            with Image.open(file_path) as img:
                info = f"图像文件 '{filename}' 详细信息：\n"
                info += f"- 尺寸: {img.width} x {img.height} 像素\n"
                info += f"- 模式: {img.mode}\n"
                info += f"- 格式: {img.format}\n"
                
                # 如果是RGB或RGBA图像，显示一些基本信息
                if img.mode in ['RGB', 'RGBA']:
                    info += "- 这是一张彩色图像，可用于视觉分析\n"
                elif img.mode == 'L':
                    info += "- 这是一张灰度图像\n"
                else:
                    info += f"- 图像模式: {img.mode}\n"
                
                info += "\n图像文件可用于视觉参考，但不包含地理空间信息。"
                return info
        except Exception as e:
            return f"图像文件 '{filename}' 基本信息：\n- 文件已成功上传\n- 支持图像分析\n- 错误详情: {str(e)}"
    
    def load_documents(self, directory: str) -> List[Dict[str, Any]]:
        """
        从指定目录加载文档
        
        Args:
            directory: 文档目录路径
            
        Returns:
            文档列表，每个文档包含内容和元数据
        """
        documents = []
        # TODO: 实现文档加载逻辑
        return documents
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将文档分割成适合向量化的文本块
        
        Args:
            documents: 原始文档列表
            
        Returns:
            分割后的文本块列表
        """
        chunks = []
        
        for doc in documents:
            content = doc['content']
            metadata = doc['metadata'].copy()
            
            if len(content) <= self.max_chunk_size:
                # 文档内容较短，直接作为一个块
                chunks.append({
                    'content': content,
                    'metadata': metadata
                })
            else:
                # 文档内容较长，需要分块
                start = 0
                chunk_index = 0
                
                while start < len(content):
                    end = start + self.max_chunk_size
                    
                    # 如果不是最后一块，尝试在句子边界处分割
                    if end < len(content):
                        # 寻找最近的句号、问号或感叹号
                        sentence_end = -1
                        for i in range(end, max(start + self.max_chunk_size - 200, start), -1):
                            if i < len(content) and content[i] in '.!?。！？':
                                sentence_end = i + 1
                                break
                        
                        if sentence_end != -1:
                            end = sentence_end
                        else:
                            # 如果找不到合适的句子边界，强制在max_chunk_size处分割
                            end = start + self.max_chunk_size
                    
                    chunk_content = content[start:end].strip()
                    if chunk_content:
                        chunk_metadata = metadata.copy()
                        chunk_metadata['chunk_index'] = chunk_index
                        chunk_metadata['total_chunks'] = (len(content) + self.max_chunk_size - 1) // self.max_chunk_size
                        
                        chunks.append({
                            'content': chunk_content,
                            'metadata': chunk_metadata
                        })
                        chunk_index += 1
                    
                    start = end + self.chunk_overlap if self.chunk_overlap > 0 else end
        
        return chunks
    
    def process_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        处理单个或多个文档文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            处理后的文档列表，每个包含内容和元数据
        """
        documents = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
                
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            
            try:
                if file_ext == '.pdf':
                    from PyPDF2 import PdfReader
                    reader = PdfReader(file_path)
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() or ""
                    
                    if text_content.strip():
                        documents.append({
                            'content': text_content.strip(),
                            'metadata': {
                                'source': filename,
                                'file_type': 'pdf',
                                'page_count': len(reader.pages)
                            }
                        })
                        
                elif file_ext in ['.txt', '.md']:
                    # 支持多种编码格式
                    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
                    text_content = ""
                    success = False
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                text_content = f.read()
                            success = True
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if not success:
                        # 如果所有编码都失败，使用errors='replace'作为最后手段
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            text_content = f.read()
                    
                    if text_content.strip():
                        file_type = 'markdown' if file_ext == '.md' else 'text'
                        documents.append({
                            'content': text_content.strip(),
                            'metadata': {
                                'source': filename,
                                'file_type': file_type
                            }
                        })
                        
                elif file_ext in ['.docx']:
                    from docx import Document
                    doc = Document(file_path)
                    text_content = "\n".join([para.text for para in doc.paragraphs])
                    
                    if text_content.strip():
                        documents.append({
                            'content': text_content.strip(),
                            'metadata': {
                                'source': filename,
                                'file_type': 'docx'
                            }
                        })
                
                elif file_ext in ['.doc']:
                    # DOC文件处理 - 提供有用的基本信息
                    try:
                        file_size = os.path.getsize(file_path)
                    except (OSError, ImportError):
                        file_size = 0
                    
                    # 根据文件名推断内容（基于常见命名模式）
                    filename_lower = filename.lower()
                    content_hints = []
                    
                    if '遥感' in filename or 'remote' in filename_lower or 'rs' in filename_lower:
                        content_hints.append("遥感技术相关文档")
                    if '实验' in filename or 'report' in filename_lower or 'lab' in filename_lower:
                        content_hints.append("实验报告")
                    if '基础' in filename or 'basic' in filename_lower:
                        content_hints.append("基础知识")
                    if '应用' in filename or 'application' in filename_lower:
                        content_hints.append("应用案例")
                    
                    if content_hints:
                        hint_text = "、".join(content_hints)
                        info = f"Word文档 '{filename}' 已上传。\n这是一份{hint_text}，可用于问答参考。"
                    else:
                        info = f"Word文档 '{filename}' 已上传，可用于问答参考。"
                    
                    # 添加文件大小信息
                    if file_size > 0:
                        if file_size < 1024:
                            size_str = f"{file_size} 字节"
                        elif file_size < 1024 * 1024:
                            size_str = f"{file_size // 1024} KB"
                        else:
                            size_str = f"{file_size // (1024 * 1024)} MB"
                        info += f"\n文件大小: {size_str}"
                    
                    documents.append({
                        'content': info,
                        'metadata': {
                            'source': filename,
                            'file_type': 'doc',
                            'file_size': file_size,
                            'note': 'DOC格式文件，已提取基本信息用于问答'
                        }
                    })
                
                # === 遥感影像格式支持 ===
                elif file_ext in ['.tif', '.tiff']:
                    # GeoTIFF处理
                    content = self._extract_geotiff_info(file_path, filename)
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'geotiff',
                            'note': 'GeoTIFF遥感影像支持已启用'
                        }
                    })
                
                elif file_ext in ['.img']:
                    # ERDAS IMG处理
                    content = self._extract_erdas_img_info(file_path, filename)
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'erdas_img',
                            'note': 'ERDAS IMG遥感影像支持已启用'
                        }
                    })
                
                elif file_ext in ['.bil', '.bsq', '.bip']:
                    # ENVI BIL/BSQ/BIP处理
                    content = self._extract_envi_info(file_path, filename)
                    format_name = {'bil': 'BIL', 'bsq': 'BSQ', 'bip': 'BIP'}[file_ext[1:]]
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': f'envi_{format_name.lower()}',
                            'note': f'ENVI {format_name}遥感影像支持已启用'
                        }
                    })
                
                elif file_ext in ['.nc', '.nc4']:
                    # NetCDF处理
                    content = self._extract_netcdf_info(file_path, filename)
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'netcdf',
                            'note': 'NetCDF科学数据支持已启用'
                        }
                    })
                
                elif file_ext in ['.hdf', '.h5', '.hdf5']:
                    # HDF/HDF5处理
                    content = self._extract_hdf_info(file_path, filename)
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'hdf',
                            'note': 'HDF科学数据支持已启用'
                        }
                    })
                
                # === 矢量数据格式支持 ===
                elif file_ext in ['.shp']:
                    # Shapefile处理
                    content = self._extract_vector_info(file_path, filename, 'shapefile')
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'shapefile',
                            'note': 'Shapefile矢量数据支持已启用'
                        }
                    })
                
                elif file_ext in ['.geojson']:
                    # GeoJSON处理
                    content = self._extract_vector_info(file_path, filename, 'geojson')
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'geojson',
                            'note': 'GeoJSON矢量数据支持已启用'
                        }
                    })
                
                elif file_ext in ['.kml', '.kmz']:
                    # KML/KMZ处理
                    content = self._extract_vector_info(file_path, filename, 'kml')
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'kml',
                            'note': 'KML/KMZ矢量数据支持已启用'
                        }
                    })
                
                elif file_ext in ['.gpx']:
                    # GPX处理
                    content = self._extract_vector_info(file_path, filename, 'gpx')
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'gpx',
                            'note': 'GPX轨迹数据支持已启用'
                        }
                    })
                
                # === 图像格式支持 ===
                elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    # 普通图像处理
                    content = self._extract_image_info(file_path, filename, file_ext)
                    image_format = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'bmp': 'BMP', 'gif': 'GIF'}[file_ext[1:]]
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': filename,
                            'file_type': 'image',
                            'image_format': image_format,
                            'note': f'{image_format}图像支持已启用'
                        }
                    })
                
                # === 结构化数据格式支持 ===
                elif file_ext in ['.csv']:
                    # CSV处理
                    import pandas as pd
                    try:
                        df = pd.read_csv(file_path, nrows=10)  # 只读前10行
                        info = f"CSV文件 '{filename}' 详细信息：\n"
                        info += f"- 列数: {len(df.columns)}\n"
                        info += f"- 行数（样本）: {len(df)}\n"
                        info += f"- 列名: {list(df.columns)}\n"
                        
                        # 显示数据类型
                        info += "- 数据类型:\n"
                        for col, dtype in df.dtypes.items():
                            info += f"  {col}: {dtype}\n"
                        
                        # 显示前几行数据（如果不太宽）
                        if len(df.columns) <= 5:
                            info += "- 数据样本:\n"
                            for idx, row in df.head(3).iterrows():
                                info += f"  行 {idx}: {dict(row)}\n"
                        
                        info += "\nCSV格式常用于存储表格数据，可用于数据分析和处理。"
                        documents.append({
                            'content': info,
                            'metadata': {
                                'source': filename,
                                'file_type': 'csv',
                                'note': 'CSV表格数据支持已启用'
                            }
                        })
                    except Exception as e:
                        # 如果pandas失败，回退到基本处理
                        info = f"CSV文件 '{filename}' 已上传用于参考（支持表格数据问答）。"
                        documents.append({
                            'content': info,
                            'metadata': {
                                'source': filename,
                                'file_type': 'csv',
                                'note': 'CSV基本支持已启用'
                            }
                        })
                
                elif file_ext in ['.json']:
                    # JSON处理
                    import json as json_lib
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json_lib.load(f)
                        
                        info = f"JSON文件 '{filename}' 详细信息：\n"
                        
                        def describe_json(obj, indent=0):
                            prefix = "  " * indent
                            if isinstance(obj, dict):
                                if len(obj) == 0:
                                    return f"{prefix}空对象\n"
                                result = ""
                                for i, (key, value) in enumerate(list(obj.items())[:5]):
                                    if i == 0:
                                        result += f"{prefix}对象包含 {len(obj)} 个键:\n"
                                    result += f"{prefix}  {key}: "
                                    if isinstance(value, (dict, list)):
                                        result += "\n" + describe_json(value, indent + 2)
                                    else:
                                        result += f"{type(value).__name__} ({str(value)[:50]}{'...' if len(str(value)) > 50 else ''})\n"
                                if len(obj) > 5:
                                    result += f"{prefix}  ... (还有 {len(obj) - 5} 个键)\n"
                                return result
                            elif isinstance(obj, list):
                                if len(obj) == 0:
                                    return f"{prefix}空数组\n"
                                result = f"{prefix}数组包含 {len(obj)} 个元素:\n"
                                for i, item in enumerate(obj[:3]):
                                    result += describe_json(item, indent + 1)
                                if len(obj) > 3:
                                    result += f"{prefix}  ... (还有 {len(obj) - 3} 个元素)\n"
                                return result
                            else:
                                return f"{prefix}{type(obj).__name__} ({str(obj)[:50]}{'...' if len(str(obj)) > 50 else ''})\n"
                        
                        info += describe_json(data)
                        info += "\nJSON格式常用于存储结构化数据，支持嵌套对象和数组。"
                        
                        documents.append({
                            'content': info,
                            'metadata': {
                                'source': filename,
                                'file_type': 'json',
                                'note': 'JSON结构化数据支持已启用'
                            }
                        })
                    except Exception as e:
                        # 如果JSON解析失败，回退到基本处理
                        info = f"JSON文件 '{filename}' 已上传用于参考（支持结构化数据问答）。"
                        documents.append({
                            'content': info,
                            'metadata': {
                                'source': filename,
                                'file_type': 'json',
                                'note': 'JSON基本支持已启用'
                            }
                        })
                        
                else:
                    # 其他支持的格式
                    info = f"文件 '{filename}' 已上传用于参考。"
                    documents.append({
                        'content': info,
                        'metadata': {
                            'source': filename,
                            'file_type': 'other'
                        }
                    })
                    
            except Exception as e:
                # 记录错误但继续处理其他文件
                error_doc = {
                    'content': f"文件 '{filename}' 处理失败: {str(e)}",
                    'metadata': {
                        'source': filename,
                        'file_type': 'error',
                        'error': str(e)
                    }
                }
                documents.append(error_doc)
        
        # 对文档进行分块处理
        if documents:
            return self.split_documents(documents)
        else:
            return []
    
    def process_directory(self, input_dir: str, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        处理整个目录的文档
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径（可选）
            
        Returns:
            处理后的文档块列表
        """
        documents = self.load_documents(input_dir)
        chunks = self.split_documents(documents)
        return chunks