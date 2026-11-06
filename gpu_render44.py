import os,ctypes,time,itertools,math,ctypes
import sdl3

import numpy as np
from numba import jit,prange,config, threading_layer,set_num_threads,vectorize,guvectorize,float32
set_num_threads(2)



config.THREADING_LAYER = 'tbb'
print(threading_layer())
def read_file(file):
    return open(file,'r').read()

def reload_config():
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini")
    window_width = int(config["graphics"]["window_width"])
    window_height = int(config["graphics"]["window_height"])

    return window_width,window_height

window_width,window_height=600,600


window_width_half=window_width/2
window_height_half=window_height/2
 

print(sdl3.SDL_GetDisplays(None))


if __name__ == "__main__":
    print(os.getcwd())
    

def sdl_get_version(Version):
    print(sdl3.SDL_VERSIONNUM_MAJOR(Version),sdl3.SDL_VERSIONNUM_MINOR(Version),sdl3.SDL_VERSIONNUM_MICRO(Version))

sdl_get_version(sdl3.SDL_GetVersion())

print(sdl3.SDL_GetPlatform().decode())
print(sdl3.SDL_GetCPUCacheLineSize())


result=sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO | sdl3.SDL_INIT_AUDIO)

if result==False:
    print(f"failed to initialize library: {sdl3.SDL_GetError().decode()}.")
window = sdl3.SDL_CreateWindow(b"game", window_width, window_height, sdl3.SDL_WINDOW_RESIZABLE)
renderDrivers = [sdl3.SDL_GetRenderDriver(i).decode() for i in range(sdl3.SDL_GetNumRenderDrivers())]
print(renderDrivers)
if renderDrivers=='software':
     print("note: you are using software mod please get a gpu :(")
renderer =  sdl3.SDL_CreateRenderer(window, ("vulkan").encode())

gpus=sdl3.SDL_GetNumGPUDrivers()
if gpus>1:
    print(sdl3.SDL_GetGPUDriver(1).decode(),sdl3.SDL_GetGPUDriver(0).decode())
    print('2d elments can be offloaded')



def load_image_to_gpu(renderer,image_path):
    surface = sdl3.SDL_LoadBMP(b'assets/textures/'+image_path)
    return sdl3.SDL_CreateTextureFromSurface(renderer, surface) 

pre_indices = np.array([ 
            [1, 5, 3],  # i_val=1, 5, 3
            [2, 3, 6],  # i_val=2, 3, 6
            [3, 2, 1],  # i_val=3, 2, 1
            [4, 6, 5],  # i_val=4, 6, 5
            [5, 1, 4],  # i_val=5, 1, 4
            [6, 4, 2],  # i_val=6, 4, 2
            ], dtype=np.int32)-1

texture_array=[b'red.bmp',b'blue.bmp',b'green.bmp',b'yellow.bmp',b'orange.bmp',b'purple.bmp']
for I in range(6):
    texture_array[I]=load_image_to_gpu(renderer,image_path=texture_array[I])

def leading_trues(arr: np.ndarray) -> int:
    return np.argmax(~arr) if not arr.all() else len(arr)

def range_check(x,y,z,shape):
    if x==0 or y==0 or z==0 or shape[0]==x or shape[1]==y or shape[0]==z:
        return False
    else:
        return True
        
def look(shape,x,y,z):
    location=[[x,y,z],[x+1,y,z],[x,y+1,z],[x,y,z+1],[x-1,y,z],[x,y-1,z],[x,y,z-1]]
    for I in range(7):
        x,y,z=location[I]
        if range_check(x,y,z,shape)==False:
            return False
    return True

def sort_list_z(list1,list2):
    return [list1[i] for i in np.argsort(list2,)]

class fighters():
    def __init__(self,type,origin):
        self.origin=origin
        self.hp=100
        self.xyz=np.zeros(21, dtype=np.float32)
        

class squadron():
    def __init__(self,list):
        self.list=list
        self.xyz=0
        for I in range(self.list):
            self.list.speed*=1,1
    def render(self):
        print("hi")
    def tick(self):
        print("hi")

    @staticmethod
    def destory(self):
        for I in range(self.list):
            self.list.speed/=1.1


class System():
    def __init__(self):
        self.object_list=[]
        self.object_list_len=0
        self.total_objects=0

        self.cp=np.zeros( shape=(1, 3, 6)) 
        self.pp=np.zeros( shape=(1, 3)) 
        self.xyz=np.zeros(shape=(1,3))
        self.mask =np.zeros( shape=(1,6))

        self.the_offset=np.array([window_width_half,window_height_half])
        self.pre_dirs_gpu = np.array([0, 1, 2, 2, 1, 0])
        self.pre_factors_gpu = np.array([1.0, 1.0, -1.0, 1.0, -1.0, -1.0])

   
        self.tick = np.zeros(1)
        self.tick[0]=True

    def system_add_object(self,__object__s):
    
        total=len(__object__s)
        for I in range(total):
            self.object_list.append(__object__s[I])
            if __object__s[I].__class__.__name__ == "ship":
                self.total_objects+=__object__s[I].total
            else:
                self.total_objects+=1
        self.object_list_len+=total

        print(self.total_objects) 
        self.cp=np.zeros( shape=(self.total_objects, 3, 8))
        self.cp2=np.zeros(shape=(self.total_objects, 3, 8)) #corners

        self.pp=np.zeros(shape=(self.total_objects, 3)) #pivot point
        self.xyz=np.zeros(shape=(self.total_objects,3))
        self.mask=np.zeros(shape=(self.total_objects,3))
        self.size=np.zeros(shape=(self.total_objects,3))

        #self.check=np.array(ti.uint1, shape=(self.total_objects))

        self.id_list=np.zeros( shape=(self.total_objects))
        self.z_list=np.zeros( shape=(self.total_objects))

        store1,store2,store3=[None]*S.total_objects,[None]*S.total_objects,[None]*S.total_objects
        for I in range(S.object_list_len):
            if self.object_list[I].__class__.__name__ == "ship":
                for II in range(self.object_list[I].total):
                    cache=I+II
                    store1[cache]=self.object_list[I].list[II].size
                    store2[cache]=self.object_list[I].list[II].pivot_point
                    store3[cache]=self.object_list[I].list[II].xyz
            else:
                store1[I]=self.object_list[I].size
                store2[I]=self.object_list[I].pivot_point
                store3[I]=self.object_list[I].xyz

        self.size=np.stack(store1)
        self.pp=np.stack(store2)
        self.xyz=np.stack(store3)
        
        
        self.lookup_gpu = np.array([[5,0],[4,1],[2,3]])
        self.corners_3d=np.array([[  -1.,  1. ,-1. , 1., -1.,  1.],
                                  [   1., -1. ,-1. , 1. , 1. ,-1.],
                                  [   1.,  1.,  1. ,-1., -1., -1.]])
    def gpu(self,r_matrix_):
        roate_matrix=r_matrix_
        
        z=Main_camera.xyz[2]
        for I in range(self.total_objects):
            local_mask=np.array([roate_matrix[2, 0],roate_matrix[2, 1],roate_matrix[2, 2]])
            local_pp=np.array([self.pp[I,0],self.pp[I,1],self.pp[I,2]])
            local_cp=np.array([[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]])

            
            
            #tick
            if self.tick[0]==True:
                for II in range(3):
                    for III in range(6):
                        self.cp2[I,II,III]=self.corners_3d[II,III]*self.size[I,II]
            #tick
            
            for II in range(3):
                if (local_mask[II] < 0 )==1:
                    local_mask[II]=self.lookup_gpu[II,1]
                else:
                    local_mask[II]=self.lookup_gpu[II,0]
                for III in range(6):
                    local_cp[II,III]=self.cp2[I,II,III]


            local_cp=rotate_matrix_gpu(local_cp,roate_matrix,local_pp,Main_camera.xyz)

            xy=np.array([self.xyz[I,0],self.xyz[I,1]])
            local_cp=projection_gpu(xy,1/z,local_cp,Main_camera.xyz,self.the_offset)
            
            for II in range(3):
                self.mask[I,II]=local_mask[II]
            for III in range(6):
                for II in range(2):
                    self.cp[I,II,III]= local_cp[II,III]
        return None
    

#@jit(nopython=True,fastmath=True,cache=True)
def rotate_matrix_gpu(matrix,roate_matrix,pivot_point,xyz):
    for I in range(3):
        for II in range(6):
            matrix[I,II]=matrix[I,II]-(pivot_point[I]+xyz[I])
    matrix=roate_matrix@matrix
    for I in range(2):
        for II in range(6):
            matrix[I,II]+=(pivot_point[I]+xyz[I])
    return matrix  


@vectorize(fastmath=True)
def multiply_scalars(x,z):
    return corners+1

@jit(nopython=True,fastmath=True,cache=True,parallel=False,boundscheck=False)
def projection_gpu(xy,z,corners,Main_camera_xy,offset):
    for I in prange(2):
        add_vecotor=xy[I]
        for II in prange(6):
            corners[I,II]=(corners[I,II]+add_vecotor)*z#+offset[I]
    return corners



cache=sdl3.SDL_CreateTexture(renderer, sdl3.SDL_PIXELFORMAT_RGBA32, sdl3.SDL_TEXTUREACCESS_TARGET, window_width,window_height)
#sdl3.SDL_SetTextureBlendMode(cache, sdl3.SDL_BLENDMODE_BLEND_PREMULTIPLIED)
r2=sdl3.SDL_FRect(0,0,0,0)

def render(object_list,delay):
    global cache
    sdl3.SDL_SetRenderDrawColorFloat(renderer, 0,0,255, 150)
    sdl3.SDL_RenderClear(renderer)

    if Main_camera.angle_xyz_last[0]==Main_camera.angle_xyz[0]  and Main_camera.angle_xyz_last[1]==Main_camera.angle_xyz[1]:
        camera_test=True
    else:
        camera_test=False


    r_matrix_ = np.zeros((3, 3), dtype=np.float32)
    calculate_matrix_rotate_3(Main_camera.angle_xyz,r_matrix_)
    S.gpu(r_matrix_)
  
    corners=S.cp
    mask=S.mask
    
    #object_list[I].__class__.__name__
    test=0
    for I in range(S.object_list_len):
        if test == 1:
            if camera_test==False:
                sdl3.SDL_SetRenderTarget(renderer, object_list[I].texture_cache)
        
                sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0)
                sdl3.SDL_RenderClear(renderer)

                for II in range(object_list[I].total):
                    object_list[I].list[II].render(renderer,mask[I+II],corners[I+II])
                    sdl3.SDL_SetRenderTarget(renderer, None)
                sdl3.SDL_RenderTexture(renderer,object_list[I].texture_cache,None,r4)
        else:
            corners[I,0]+=S.the_offset[0]
            corners[I,1]+=S.the_offset[1]
            
            sdl3.SDL_SetRenderTarget(renderer, cache)
            sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0)
            sdl3.SDL_RenderClear(renderer)
      
            render_cube(renderer,mask[I],corners[I])
            sdl3.SDL_SetRenderTarget(renderer,None)
            r2=sdl3.SDL_FRect(0,0,window_width,window_height)

            #matrix_3=matrix_test(global_matrix,r_matrix_,Main_camera.xyz)
            
            matrix_3=matrix_2(r_matrix_,Main_camera.xyz)
            #print(matrix_3)
            vals, counts = np.unique(matrix_3, return_counts=True)

            # Filter values where count is greater than 1
            duplicates = vals[counts > 1]

            print("Duplicate values:", duplicates)
            w_width = window_width
            w_height = window_height
            n = len(matrix_3)
            pts = np.asarray(matrix_3, dtype=np.float32)[:, :2]  
            x = pts[:, 0]
            y = pts[:, 1]

            q = vbuf[:n]
            q[:, 0, 0] = x;           q[:, 0, 1] = y
            q[:, 1, 0] = x;           q[:, 1, 1] = y + w_height
            q[:, 2, 0] = x + w_width; q[:, 2, 1] = y
            q[:, 3, 0] = x + w_width; q[:, 3, 1] = y + w_height
            sdl3.SDL_RenderGeometry(renderer,cache,vertices,num_vertices,indices,num_indices)


            #for I in range(20**3):
            #    rote=matrix_3[I]
            #    r2.x,r2.y=rote[0],rote[1]
            #    sdl3.SDL_RenderTexture(renderer,cache,None,r2)
    Main_camera.angle_xyz_last[0:2]=Main_camera.angle_xyz[0:2]
    return delay 


size=2
num_quads = size**3  # 8,000 quads
num_indices = 6 * num_quads  # 48,000 total indices
num_vertices=4*num_quads

VertexArray = sdl3.SDL_Vertex *(num_vertices)
vertices = VertexArray() 
vbuf = np.frombuffer(vertices, dtype=np.float32).reshape(-1, 4, 8)

corner_tex = ((0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0))
template = (sdl3.SDL_Vertex * 4)()
for i, (u, v) in enumerate(corner_tex):
    template[i].position = sdl3.SDL_FPoint(0.0, 0.0)
    template[i].color = sdl3.SDL_FColor(1.0, 1.0, 1.0, 1.0)
    template[i].tex_coord = sdl3.SDL_FPoint(u, v)



quad_bytes = ctypes.sizeof(template)
for q in range(num_quads):
    ctypes.memmove(
        ctypes.addressof(vertices) + q * quad_bytes,
        ctypes.addressof(template),
        quad_bytes,
    )

#vertices = VertexArray(*base_verts)


IndexArray = ctypes.c_int * num_indices
quad_pattern = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
offsets = (np.arange(num_quads, dtype=np.int32) * 4)[:, None]
indices_np = (offsets + quad_pattern).ravel()   
indices = indices_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

#raw_indices = []
#for i in range(num_quads):
#    offset = i * 4
#    raw_indices.extend([
#        offset + 0, offset + 1, offset + 2, 
#        offset + 2, offset + 1, offset + 3
#    ])

#indices = IndexArray(*raw_indices)

#def cache_matrix(size):
#    matrix_1 = np.zeros((size**3, 3), dtype=np.float32)  
#    for I in  range(size):
#        for II in range(size):
#            for III in range(size):
#                matrix_1[I+II*size+III*size**2]=I*200,II*200,III*200
#    return matrix_1

@jit(parallel=True, cache=True)
def cache_matrix(size):
    out = np.empty((size**3, 3), dtype=np.float32)
    for III in prange(size):
        z = np.float32(III * 200)
        for II in range(size):
            y = np.float32(II * 200)
            base = (III * size + II) * size
            for I in range(size):
                row = base + I
                out[row, 0] = I * 200
                out[row, 1] = y
                out[row, 2] = z
    return out

global_matrix=cache_matrix(size=size)


@jit(nopython=True,fastmath=True,cache=True,parallel=False,boundscheck=False)
def matrix_2(r_matrix_,camera):
    matrix_C = global_matrix @ r_matrix_.T
    matrix_C[:, :2] //= camera[2]
    matrix_C = matrix_C[np.argsort(matrix_C[:, 2])]
    return matrix_C



@guvectorize(
    ["void(float64[:, :], float64[:, :], float64[:], float64[:, :])"],
    "(n,k),(k,k),(c)->(n,k)",
    nopython=True,
    fastmath=True,
    cache=True,
    boundscheck=False,
)
def matrix_test(points, r_matrix_, camera, out):
    n, k = points.shape
    c = camera[2]
    z = np.empty(n)
    for i in range(n):
        s = 0.0
        for l in range(k):
            s += points[i, l] * r_matrix_[2, l]
        z[i] = s

    order = np.argsort(z)
    for i in range(n):
        p = order[i]
        for j in range(k):
            s = 0.0
            for l in range(k):
                s += points[p, l] * r_matrix_[j, l]
            out[i, j] = s

        out[i, 0] = math.floor(out[i, 0] / c)
        out[i, 1] = math.floor(out[i, 1] / c)
            
@guvectorize([(float32[:], float32[:, :])], '(n)->(n,n)', target='parallel', cache=True)
def calculate_matrix_rotate_3(angle_xyz, res):
    cx = math.cos(angle_xyz[0])
    cy = math.cos(angle_xyz[1])
    cz = math.cos(angle_xyz[2])
    
    sx = math.sin(angle_xyz[0])
    sy = math.sin(angle_xyz[1])
    sz = math.sin(angle_xyz[2])
    
    cz_sy = cz * sy
    sz_sy = sz * sy
    
    res[0, 0] = cz * cy
    res[0, 1] = cz_sy * sx - sz * cx
    res[0, 2] = cz_sy * cx + sz * sx
    
    res[1, 0] = sz * cy
    res[1, 1] = sz_sy * sx + cz * cx
    res[1, 2] = sz_sy * cx - cz * sx
    
    res[2, 0] = -sy
    res[2, 1] = cy * sx
    res[2, 2] = cy * cx


class ship():
    def __init__(self,data,hp,xyz):
        self.hp=hp
        self.data=data
        self.xyz=xyz
        self.ship_type=0
        self.pocket=False

        self.ROT_SPEED_XYZ=np.array([.000,.000,.000],dtype=np.float32)
        self.movment=np.array([0,0,0],dtype=np.float32)
        self.angle_xyz=np.array([0,0,0],dtype=np.float32)

        self.list=[]
        self.total=0

        self.texture_cache=sdl3.SDL_CreateTexture(renderer, sdl3.SDL_PIXELFORMAT_RGBA32, sdl3.SDL_TEXTUREACCESS_TARGET, window_width,window_height)
        
        xyz_length=np.array([len(data),len(data[0]),len(data[0][0])])

        for I in  range(xyz_length[0]):
            for II in range(xyz_length[1]):
                for III in range(xyz_length[2]):
                    if data[I,II,III]==False:
                        data[I,II,III]=look(xyz_length,I,II,III)

        for I in  range(xyz_length[0]):
            for II in range(xyz_length[1]):
                for III in range(xyz_length[2]):
                    if data[I,II,III]:
                  
                        data,size=self.make_mesh(data,I,II,III,xyz_length)
                        self.total += 1
                        object_xyz=np.array([I*200, II*200, III*200],dtype=np.float32)
        
                        object_xyz+=size*100
                        self.list.append(
                            object_(
                                size=size*100,
                                xyz=object_xyz+self.xyz-xyz_length*100,  
                                movment=np.array([0., 0., 0.],dtype=np.float32),
                                angle_xyz=np.array([0, 0, 0],dtype=np.float32),
                                pivot_point=-1*object_xyz+xyz_length*100,
                                copy=False,
                                mask_inverse_overlay=0))
        print(len(self.list))            
    def make_mesh(self,data, x, y, z,xyz_length):
    
        X, Y, Z = data.shape

        # If the start voxel is empty, return nothing
        if not data[x, y, z]:
            return (0, 0, 0)

        # ----- Expand in X -----
        sx = 0
        i = x
        while i < X and data[i, y, z]:
            sx += 1
            i += 1

        # ----- Expand in Y -----
        sy = 0
        j = y
        while True:
            if j >= Y:
                break
            # Check full row in X-range must be filled
            full = True
            for i in range(x, x + sx):
                if not data[i, j, z]:
                    full = False
                    break
            if not full:
                break
            sy += 1
            j += 1

        # ----- Expand in Z -----
        sz = 0
        k = z
        while True:
            if k >= Z:
                break
            # Check full layer (X × Y) must be filled
            full = True
            for j in range(y, y + sy):
                for i in range(x, x + sx):
                    if not data[i, j, k]:
                        full = False
                        break
                if not full:
                    break
            if not full:
                break
            sz += 1
            k += 1

        # ----- Clear (set to 0) the block we just consumed -----
        data[x:x+sx, y:y+sy, z:z+sz] = False

        return data,np.array([sx, sy, sz])

    def render(self):
        tick=34
        
class object_:
    __slots__ = ("xyz","size","movment","angle_xyz","pivot_point","copy","mask_inverse_overlay","ROT_SPEED_XYZ","corners2")
    def __init__(self, 
                 size=None,
                 xyz=None,
                 movment=None,
                 angle_xyz=None,
                 pivot_point=None,
                 copy=False,
                 mask_inverse_overlay=None):
        
        self.xyz = xyz
        self.size= size
        self.copy = copy
    
        self.movment = movment
        self.angle_xyz = angle_xyz
        
        self.pivot_point = pivot_point
        self.ROT_SPEED_XYZ = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        
        if copy:
            self.mask_inverse_overlay = mask_inverse_overlay


#a=sdl3.SDL_FPoint(0,0)
#b=sdl3.SDL_FPoint(0,0)
#c=sdl3.SDL_FPoint(0,0)
def render_cube(renderer,mask=None,corners=None):
    #global a,b,c
    for i in range(3):
        pre_idx=int(mask[i])
        test1,test2 = corners[0][pre_indices[pre_idx]],corners[1][pre_indices[pre_idx]]
        sdl3.SDL_RenderTextureAffine(
                renderer, texture_array[pre_idx], None,
                sdl3.SDL_FPoint(test1[0], test2[0]),
                sdl3.SDL_FPoint(test1[1], test2[1]),
                sdl3.SDL_FPoint(test1[2], test2[2]))
    return None


class camera():
    def __init__(self, x=0,y=0,z=20):
        self.xyz=np.zeros( shape=(3))
        self.angle_xyz=np.array([0.1, 0.2, 0.3], dtype=np.float32)
        self.angle_xyz_last=np.zeros( shape=(3))

        self.movement=np.zeros(3)
        self.movement_angle=np.zeros(3)
        
        self.xyz[2]=z
    def tick(self):
        None

class keyboard_data():
    def __init__(self,keyboard_events,commands):
        self.keyboard_events=keyboard_events
        self.keyboard_events_length=len(keyboard_events)
        self.commands=eval_commpreser(commands,self.keyboard_events_length)

    def keyboard_data_parser(self,key):
        for I in range(self.keyboard_events_length):
            if key==self.keyboard_events[I]:
                print("test")
                return self.commands[I](key)
    
            
            
def io(event,event_types,event_types_len,event_command,event_data_send):
    while sdl3.SDL_PollEvent(ctypes.byref(event)):  
        for I in range(event_types_len):
            if event.type == event_types[I]:
                return_data=event_command[I](eval(event_data_send[I]))
                if return_data==False:
                     return False
    return True
    #add id eval compresser. This 11% overhead

def death(event):
    print("tewst")
    return False

def eval_commpreser(array,length):
    array2=[None]*length
    for I in range(length):
        array2[I]=eval(array[I])
    return array2 


def system_mouse_added(event):
    print("a system mouse as been added")

def mouse_movement(event):
    Main_camera.angle_xyz[0]-=event.motion.xrel/100
    Main_camera.angle_xyz[1]-=event.motion.yrel/100

def left(key):
    global object_list_len

def middle(key):
    print("middle click")
def right(key):
    print('right click')

def q(key):
    Main_camera.angle_xyz[1]-=.01
def e(key):
    Main_camera.angle_xyz[1]+=.01

def w(key):
    Main_camera.xyz[2]-=.10
def s(key):
    Main_camera.xyz[2]+=.10
def a(key):
    Main_camera.xyz[0]-=10
def d(key):
    Main_camera.xyz[0]+=10

def space(key):
    Main_camera.xyz[1]-=10
def z(key):
    Main_camera.xyz[1]+=10

S=System()
Main_camera=camera(0,0,1)

keyboard_UP=keyboard_data([sdl3.SDLK_ESCAPE],['death'])
keyboard_DOWN=keyboard_data([sdl3.SDLK_W,sdl3.SDLK_S,sdl3.SDLK_A,sdl3.SDLK_D,sdl3.SDLK_Q,sdl3.SDLK_E,sdl3.SDLK_SPACE,sdl3.SDLK_Z],['w','s','a','d','q',"e","space","z"])

Mouse_up=keyboard_data([sdl3.SDL_BUTTON_LMASK,sdl3.SDL_BUTTON_MIDDLE,sdl3.SDL_BUTTON_RIGHT],['left','middle','right'])
Mouse_down=keyboard_data([sdl3.SDL_BUTTON_LEFT,sdl3.SDL_BUTTON_MIDDLE,sdl3.SDL_BUTTON_RIGHT],['left','middle','right'])

event_types=[sdl3.SDL_EVENT_QUIT,sdl3.SDL_EVENT_KEY_UP,sdl3.SDL_EVENT_KEY_DOWN,sdl3.SDL_EVENT_MOUSE_ADDED,sdl3.SDL_EVENT_MOUSE_MOTION,sdl3.SDL_EVENT_MOUSE_BUTTON_UP,sdl3.SDL_EVENT_MOUSE_BUTTON_DOWN]
event_types_len=len(event_types)
event_command=['death','keyboard_UP.keyboard_data_parser','keyboard_DOWN.keyboard_data_parser','system_mouse_added','mouse_movement','Mouse_up.keyboard_data_parser','Mouse_down.keyboard_data_parser']
event_command=eval_commpreser(event_command,event_types_len)
event_data_send=['event.key.key','event.key.key','event.key.key','event.key.key','event','event.button.button','event.button.button']
#event_data_send=eval_commpreser(event_data_send,event_types_len)

O=object_(size=np.array([100, 100, 100]),xyz=np.array([0,0,0]),movment=np.array([0,0,0]),angle_xyz=np.array([0.,0.,0.]) ,pivot_point=np.array([0,0,0]),copy=False)
OO=object_(size=np.array([100, 100, 100]),xyz=np.array([0,200,0]),movment=np.array([0,0,0]),angle_xyz=np.array([0.,0.,0.]) ,pivot_point=np.array([0,-200,]),copy=False)
OOO=object_(size=np.array([100, 100, 100]),xyz=np.array([200,0,0]),movment=np.array([0,0,0]),angle_xyz=np.array([0.,0.,0.]) ,pivot_point=np.array([-200,0,0]),copy=False)
OOOO=object_(size=np.array([100, 100, 100]),xyz=np.array([0,0,200]),movment=np.array([0,0,0]),angle_xyz=np.array([0.,0.,0.]) ,pivot_point=np.array([0,0,-200]),copy=False)

#mine=object_(size=np.array([1000, 1000, 100]),xyz=np.array([0,2500,0]),movment=np.array([0,0,0]),angle_xyz=np.array([0.,0.,0.]) ,pivot_point=np.array([0,0,-1500]),copy=False)


shape = (75, 75, 75)

large_tf_array = np.random.choice([True, False], size=shape,p=[.1, .9])
#large_tf_array[0][0][0]=False 

#ship1=ship(
#    large_tf_array,
#    hp=100,
#    xyz=np.array([0,0,0],dtype=np.float32)) 

S.system_add_object([O])
#S.system_add_object([O,OO,OOO,OOOO])
#S.system_add_object([ship1])

#S.system_add_object([turret_base,turret_gun1,turret_gun2,turret_gun3])
#S.system_add_object([mine])

mouse_x,mouse_y=0,0
size=25

delay=0
string="".encode()

last_time=10000000
timer = time.time()

running=True
while running:
    
    running=io(sdl3.SDL_Event(),event_types,event_types_len,event_command,event_data_send)

    if sdl3.SDL_GetTicksNS()-last_time>= 10000000:
        last_time=sdl3.SDL_GetTicksNS()
        S.tick[0]=True
    else:
        S.tick[0]=False
    
    delay=render(S.object_list,delay)

    timer_new=time.time()
    string=("fps."+str(1/(timer_new-timer))).encode()
    timer = timer_new

    
    sdl3.SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255)
    sdl3.SDL_RenderDebugText(renderer, 0, 0, string)
    sdl3.SDL_RenderPresent(renderer)

sdl3.SDL_DestroyRenderer(renderer)
sdl3.SDL_DestroyWindow(window)
sdl3.SDL_Quit()



