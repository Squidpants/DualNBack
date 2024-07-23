'''Make images for dual n-back task.'''

from PIL import Image, ImageDraw, ImageFont

class ImageSet(object):
    '''Base class to produce uniform set of test images.'''

    def __init__(self: 'ImageSet', parent: 'DualNBack') -> None:
        '''Standard setting initialization.'''

        self.parent = parent

        self.background_colour = self.parent.session_settings.get_bg_colour()
        self.fixator_colour = self.parent.session_settings.get_fx_colour()
        self.target_colour = self.parent.session_settings.get_tg_colour()
        self.number_of_targets = self.parent.session_settings.\
            get_number_targets()
        self.image_dimensions = self.parent.screen_dimensions

    def __draw_image(self: 'ImageSet', target_location: int) -> object:
        '''Produce image.'''

        image_third_vert = (self.image_dimensions[1] // 3)
        vertical_padding = (image_third_vert // 8)
        image_third_hor = ((self.image_dimensions[0] // 3) - 1)
        horizontal_padding = (
            vertical_padding + ((image_third_hor - image_third_vert) // 2))

        sprite_edge_length = (image_third_vert - (vertical_padding * 2))

        out_image = Image.new(
            'RGB', self.image_dimensions, self.background_colour)

        out_image_draw = ImageDraw.ImageDraw(out_image)

        # Probably one pixel off, double check.

        out_image_draw.line(
            [((image_third_hor + horizontal_padding),
              (self.image_dimensions[1] // 2)),
             ((image_third_hor + horizontal_padding + sprite_edge_length),
              (self.image_dimensions[1] // 2))], self.fixator_colour, 5)
        out_image_draw.line(
            [((self.image_dimensions[0] // 2),
              (image_third_vert + vertical_padding)),
             ((self.image_dimensions[0] // 2),
              (image_third_vert + vertical_padding + sprite_edge_length))],
            self.fixator_colour, 5)

        if target_location != (self.number_of_targets // 2):

            hor_start = (
                ((target_location % 3) * image_third_hor) + horizontal_padding)
            vert_start = (
                ((target_location // 3) * image_third_vert) + vertical_padding)

            out_image_draw.rectangle(
                [(hor_start, vert_start),
                 ((hor_start + sprite_edge_length),
                  (vert_start + sprite_edge_length))], self.target_colour)

        del(out_image_draw)

        return out_image

    def create_set_of_images(self: 'ImageSet') -> None:
        '''Make and save all nine images.'''

        for i in range(self.number_of_targets + 1):

            image = self.__draw_image(i)
            image.save(('images\screen' + str(i) + '.png'))

if __name__ == '__main__':

    raise ChildProcessError