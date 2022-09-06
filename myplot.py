from __future__ import annotations
from msilib import sequence
import matplotlib.pyplot as plt 
from typing import Any, Literal, Optional, Sequence, Type, TypeVar, Union
import numpy as np
from mpl_toolkits.mplot3d.art3d import PolyCollection
import itertools

LINE_WIDTH = 5
rc_params = {
    'figure':{
        'figsize':(19.20,10.80)
    },
    'font':{
            'family':'Arial',
            'size':45,
            'weight':'bold',
        },
    'axes':{
            'spines.right':False,
            'spines.top':False,
            'linewidth':LINE_WIDTH
        },
    'xtick':{
        'major.width':LINE_WIDTH,
        'major.size':15
    },
    'ytick':{
        'major.width':LINE_WIDTH,
        'major.size':15
    }
}

T = TypeVar('T', int, float)
def waterfall_plot(ax_3d, dim_2_array:np.ndarray, extent:tuple[T, T, T, T],
                   edgecolors:str|Sequence[str]='k', fill:Optional[bool]=False,
                   facecolors:str|Sequence[str]='w', alpha:float|int=1, zmin:float|int=0):
    y_len , x_len ,  = dim_2_array.shape
    x_min , x_max , y_min , y_max = extent
    xs = np.linspace(x_min,x_max,x_len)
    ys = np.linspace(y_min,y_max,y_len)
    verts:list[Any] = []
    ims:list[Any] = []
    for ydir in range(y_len):
        zs = dim_2_array[ydir]
        if fill:
            verts.append(list(zip(np.hstack((xs[0],xs,xs[-1])),np.hstack((zmin,zs,zmin)))))
        else:
            im = ax_3d.plot(xs,np.full(xs.shape,ys[ydir]),zs,c=edgecolors if type(edgecolors) is str or edgecolors is None else edgecolors[ydir])
            ims.append(*im)
    if fill:
        polygon = PolyCollection(verts,edgecolors=edgecolors,facecolors=facecolors,alpha=alpha)
        ims = ax_3d.add_collection3d(polygon,zs=ys,zdir='y')
        ax_3d.set(xlim=[x_min,x_max],ylim=[y_min,y_max],zlim=[dim_2_array.min(),dim_2_array.max()])
    return ims

KwsType = dict[Literal['bar_kw', 'err_kw', 'scatter_kw'], dict[str, Any]]
def error_plot(dataset:Sequence[Sequence[int|float]], ax, colors:str|Sequence[str]='k', scatter_shift_nums:float|Sequence[float]=0.1, 
                error_type:Literal['SD', 'SE']='SD', custom_kws:Optional[KwsType]=None) -> None: #datasetの次元に注意．行の数だけ棒グラフが描画される．
    flat = itertools.chain.from_iterable
    row_num = len(dataset); col_nums = [len(arr) for arr in dataset] #行ごとの列の数
    if isinstance(scatter_shift_nums, float): 
        scatter_shift_nums = [scatter_shift_nums]*row_num #キャスト
    bar_xs = range(row_num)
    scatter_xs =  tuple(flat([[x+shift_num]*x_len for x, x_len, shift_num in zip(bar_xs, col_nums, scatter_shift_nums)])) #散布図はscatter_shift_numだけずらすとエラーバーが見やすい
    scatter_colors = tuple(flat([[color]*x_len for color, x_len in zip(colors, col_nums)])) if not isinstance(colors, str)  else colors
    aves = [np.mean(arr) for arr in dataset] #行ごとにの列の数が異なる可能性があるため，それぞれの行に分解してmean, stdを使う必要がある．np.mean(dataset, axis=1)だとエラー
    errors = [np.std(arr) for arr in dataset]
    if error_type == 'SE':
        errors = [err / np.sqrt(x_len) for err, x_len in zip(errors, col_nums)]
    
    #デフォルトの各プロットオプション
    bar_kw = {
            'edgecolor':colors,
            'fill':False,
            'color':colors,
            'linewidth':LINE_WIDTH,
        }
    err_kw = {
            'yerr':errors,
            'capsize':10,
            'capthick':5,
            'elinewidth':LINE_WIDTH,
            'fmt':'none',
            'ecolor':'k',
        }
    scatter_kw = {
        'color':scatter_colors,
        's':150
        }
    
    #custom_kwsが設定されたときはキーワードの追加または上書き
    if custom_kws is not None:
       bar_kw = {**bar_kw, **custom_kws['bar_kw']} if 'bar_kw' in custom_kws else bar_kw
       err_kw = {**err_kw, **custom_kws['err_kw']} if 'err_kw' in custom_kws else err_kw
       scatter_kw = {**scatter_kw, **custom_kws['scatter_kw']} if 'scatter_kw' in custom_kws else scatter_kw
    
    ax.bar(bar_xs, aves, **bar_kw)
    ax.errorbar(bar_xs, aves, **err_kw)
    ax.scatter(scatter_xs, tuple(flat(dataset)), **scatter_kw)
    ax.set(xticks=bar_xs)

def plot_3d_spectrogram(ax_3d, array:np.ndarray, N:int, fs:float, window_size:int, step:int) -> None:
    freq_mesh = [fs*k / window_size for k in range(window_size//2 + 1)]
    time_mesh = np.linspace(0,N*(1/fs),(N-window_size)//step)
    X , Y = np.meshgrid(time_mesh,freq_mesh)
    Z = array.T
    ax_3d.plot_surface(X,Y,Z,cmap='terrain')
    
if __name__ == '__main__':
    for group, values in rc_params.items(): plt.rc(group, **values)
    sample_dataset = np.random.rand(2, 15)
    fig, axes = plt.subplots(1, 2)
    error_plot(sample_dataset, axes[0], colors='k', error_type='SE', scatter_shift_nums=0.5, custom_kws={
        'bar_kw':{
            'hatch':['//', '**']
        },
        'scatter_kw':{
            'edgecolor':'k',
            'linewidth':2
        },
        'err_kw':{
            'capsize':50
        }
    })
    error_plot(sample_dataset, axes[1], error_type='SE')
    for ax, title in zip(axes, ('custom', 'default')): ax.set(title=title, xlabel='data±SE', xticklabels=('data1', 'data2'))
    fig.tight_layout()
    plt.show()
    