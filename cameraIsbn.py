import io
import time
import threading
import picamera
from PIL import Image
import zbar

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []
count = 0
isbn = []
# setup timeout
timeout = time.time() + 30  #30seconds
#setup zbar
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        global count
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.name = 'Processor %d' % count
        count = count + 1
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done
        global isbn
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    pil = Image.open(self.stream)
                    pil = pil.convert('L')
                    width, height = pil.size
                    raw = pil.tostring()

                    # wrap image data
                    image = zbar.Image(width, height, 'Y800', raw)

                    print self.name + ' is scanning...'

                    # scan the image for barcodes
                    scanner.scan(image)
                    for symbol in image:
                        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
                        isbn.append(symbol.data)
                        done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    del(image)
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    while not done and time.time() < timeout:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.1)

def scanForIsbn():
    #reinitialize everything
    global count
    count = 0
    global done
    done = False
    global isbn
    isbn = []
    # setup timeout
    global timeout
    timeout = time.time() + 30  #30seconds

    with picamera.PiCamera() as camera:
        global pool
        pool = [ImageProcessor() for i in range(4)]
        camera.resolution = (640, 480)
        camera.framerate = 30
        #camera.start_preview()
        time.sleep(2)
        camera.capture_sequence(streams(), use_video_port=True)
    
    # Shut down the processors in an orderly fashion
    while pool:
        with lock:
            processor = pool.pop()
        processor.terminated = True
        processor.join()
    # check to see if we have a return value
    return isbn

if __name__ == "__main__":
    readIsbn = scanForIsbn()
    print readIsbn
    print pool
    readIsbn = scanForIsbn()
    print readIsbn
