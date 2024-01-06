import pyopencl as cl
import numpy as np

# Create a context and a command queue
context = cl.create_some_context()
queue = cl.CommandQueue(context)

# Define an OpenCL function
opencl_function = """
__kernel void square(__global float* data) {
    int gid = get_global_id(0);
    data[gid] = data[gid] * data[gid];
}
"""

# Compile the function
program = cl.Program(context, opencl_function).build()

# Create some data
data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
data_buffer = cl.Buffer(context, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=data)

# Execute the function
program.square(queue, data.shape, None, data_buffer)

# Copy the result back to the host
cl.enqueue_copy(queue, data, data_buffer)

print(data)