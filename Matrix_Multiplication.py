import random
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import matplotlib.animation as animation

size = 100          
thread_count = 8     
out_file = "100x100.mp4"


def make_matrix(rows, cols, seed):
    rnd = random.Random(seed)
    m = []
    for i in range(rows):
        row = [rnd.randint(0, 9) for j in range(cols)]
        m.append(row)
    return m


def do_one_cell(A, B, C, i, j):
    s = 0
    for k in range(len(B)):
        s += A[i][k] * B[k][j]
    C[i][j] = s


def multiply_with_threads(A, B):
    rows = len(A)
    cols = len(B[0])
    C = [[0] * cols for _ in range(rows)]

    pool = ThreadPoolExecutor(max_workers=thread_count)
    tasks = []
    for i in range(rows):
        for j in range(cols):
            tasks.append(pool.submit(do_one_cell, A, B, C, i, j))

    for t in tasks:
        t.result()

    pool.shutdown()
    return C

def make_the_video(A, B):
    A_arr = np.array(A, dtype=float)
    B_arr = np.array(B, dtype=float)

    fig, axs = plt.subplots(1, 3, figsize=(12, 4.8))
    fig.suptitle(f"Matrix Multiplication in Action ({size}x{size}, {thread_count} Threads)",
                 fontsize=13, fontweight="bold")

    caption_text = fig.text(0.5, 0.90, "", ha="center", fontsize=10)

    axs[0].imshow(A_arr, cmap="Blues")
    axs[0].set_title("A")
    axs[1].imshow(B_arr, cmap="Greens")
    axs[1].set_title(" B")
    axs[2].set_title("C ")

    for a in axs:
        a.set_xticks([])
        a.set_yticks([])

    reveal_grid = np.full((size, size), np.nan)
    orange_map = matplotlib.colormaps.get_cmap("Oranges").copy()
    orange_map.set_bad(color="white")
    c_plot = axs[2].imshow(reveal_grid, cmap=orange_map, vmin=0, vmax=1)

    def animate_step(frame_num):
        reveal_grid[frame_num, :] = 1  
        c_plot.set_data(reveal_grid)
        pct = (frame_num + 1) / size * 100
        caption_text.set_text(
            "Row {} of Matrix A, Matrix B -> Row {} of Result Matrix C   Progress: {:.1f}%".format(
                frame_num, frame_num, pct
            )
        )
        return [c_plot, caption_text]

    anim = animation.FuncAnimation(fig, animate_step, frames=size, interval=60)
    writer = animation.FFMpegWriter(fps=15, bitrate=1800)
    anim.save(out_file, writer=writer)
    plt.close(fig)


def main():
    A = make_matrix(size, size, 7)
    B = make_matrix(size, size, 13)

    start = time.time()
    C = multiply_with_threads(A, B)
    end = time.time()

    C_arr = np.array(C)
    print(C_arr[:5, :5])  
    print()

    print("Creating video")
    make_the_video(A, B)
    print()

  
    check = np.array(A) @ np.array(B)
    matches = np.array_equal(C_arr, check)

    print("-" * 65)
    print(f"[OK] {thread_count} worker threads completed {size * size} multiplication tasks")
    print(f"[OK] {size} x {size} matrices used")
    print("[OK] ThreadPoolExecutor used for multiplication")
    print("[OK] Blue x Green = Orange animation")
    print("[OK] Verification against NumPy:", "PASSED" if matches else "FAILED")
    print("-" * 65)
    print()

    print("Video created successfully:")
    print(out_file)
    print()
    print("Time taken : {:.2f} ms".format((end - start) * 1000))
    print("Matrix multiplication completed.")


if __name__ == "__main__":
    main()
