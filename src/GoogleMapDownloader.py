from PIL import Image
import math, shutil, requests, os

class GoogleMapsLayers:
  ROADMAP = "v"
  TERRAIN = "p"
  ALTERED_ROADMAP = "r"
  SATELLITE = "s"
  TERRAIN_ONLY = "t"
  HYBRID = "y"


class GoogleMapDownloader:
    """
        A class which generates high resolution google maps images given
        a longitude, latitude and zoom level
    """

    def __init__(self, lat, lng, zoom=12, layer=GoogleMapsLayers.ROADMAP):
        """
            GoogleMapDownloader Constructor
            Args:
                lat:    The latitude of the location required
                lng:    The longitude of the location required
                zoom:   The zoom level of the location required, ranges from 0 - 23
                        defaults to 12
        """
        self._lat = lat
        self._lng = lng
        self._zoom = zoom
        self._layer = layer

    def getXY(self):
        """
            Generates an X,Y tile coordinate based on the latitude, longitude
            and zoom level
            Returns:    An X,Y tile coordinate
        """

        tile_size = 256

        # Use a left shift to get the power of 2
        # i.e. a zoom level of 2 will have 2^2 = 4 tiles
        numTiles = 1 << self._zoom

        # Find the x_point given the longitude
        point_x = (tile_size / 2 + self._lng * tile_size / 360.0) * numTiles // tile_size

        # Convert the latitude to radians and take the sine
        sin_y = math.sin(self._lat * (math.pi / 180.0))

        # Calulate the y coorindate
        point_y = ((tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(
        tile_size / (2 * math.pi))) * numTiles // tile_size

        return int(point_x), int(point_y)

    def tile_to_lat_lon(self, x, y, zoom):
        """
        Converts tile coordinates to latitude and longitude.
        """
        n = 2 ** zoom
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    def get_corner_lat_lons(self, tile_width=8, tile_height=8):
        """
        Calculates the latitude and longitude of the four corners of the image.
        """
        start_x, start_y = self.getXY()
        zoom = self._zoom

        # Top-left corner
        top_left = self.tile_to_lat_lon(start_x - tile_width // 2, start_y - tile_height // 2, zoom)

        # Top-right corner
        top_right = self.tile_to_lat_lon(start_x + tile_width // 2, start_y - tile_height // 2, zoom)

        # Bottom-left corner
        bottom_left = self.tile_to_lat_lon(start_x - tile_width // 2, start_y + tile_height // 2, zoom)

        # Bottom-right corner
        bottom_right = self.tile_to_lat_lon(start_x + tile_width // 2, start_y + tile_height // 2, zoom)

        return {'top_left': top_left, 'top_right': top_right, 'bottom_left': bottom_left, 'bottom_right': bottom_right}

    def generateImage(self, **kwargs):
        """
            Generates an image by stitching a number of google map tiles together.
            Args:
                start_x:        The top-left x-tile coordinate
                start_y:        The top-left y-tile coordinate
                tile_width:     The number of tiles wide the image should be -
                                defaults to 5
                tile_height:    The number of tiles high the image should be -
                                defaults to 5
            Returns:
                A high-resolution Goole Map image.
        """

        start_x = kwargs.get('start_x', None)
        start_y = kwargs.get('start_y', None)
        tile_width = kwargs.get('tile_width', 8)
        tile_height = kwargs.get('tile_height', 8)

        # Check that we have x and y tile coordinates
        if start_x == None or start_y == None:
            start_x, start_y = self.getXY()
        # Determine the size of the image
        width, height = 256 * tile_width, 256 * tile_height
        # Create a new image of the size require
        map_img = Image.new('RGB', (width, height))
        for x in range(-tile_width//2, tile_width//2):
            for y in range(-tile_height//2, tile_height//2):
                url = f'https://mt0.google.com/vt?lyrs={self._layer}&x=' + str(start_x + x) + \
                       '&y=' + str(start_y + y) + '&z=' + str(self._zoom)
                current_tile = str(x) + '-' + str(y)
                response = requests.get(url, stream=True)
                with open(current_tile, 'wb') as out_file: shutil.copyfileobj(response.raw, out_file)
                im = Image.open(current_tile)
                map_img.paste(im, ((x+tile_width//2) * 256, (y+tile_height//2) * 256))
                os.remove(current_tile)
        print('Image size (pix): ', map_img.size)
        return map_img


# How to use:
    
# Create a new instance of GoogleMap Downloader
    
"""
LAT = YOUR_LATITUDE
LON = YOUR_LONGITUDE
ZOOM = DEFAULT IS 12

gmd = GoogleMapDownloader(LAT, LON, ZOOM, GoogleMapsLayers.SATELLITE)

print("The tile coorindates are {}".format(gmd.getXY()))

try:
    # Get the high resolution image
    img = gmd.generateImage()
except IOError:
    print("Could not generate the image - try adjusting the zoom level and checking your coordinates")
else:
    # Save the image to disk
    img.save("high_resolution_image.png")
    print("The map has successfully been created")
"""