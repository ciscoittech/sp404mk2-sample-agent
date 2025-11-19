
import {
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Avatar,
  TableContainer,
  Stack,
  Rating,
} from '@mui/material';

import user1 from 'src/assets/images/profile/user-1.jpg';
import user2 from 'src/assets/images/profile/user-2.jpg';
import user3 from 'src/assets/images/profile/user-3.jpg';
import user4 from 'src/assets/images/profile/user-4.jpg';
import user5 from 'src/assets/images/profile/user-5.jpg';
import user6 from 'src/assets/images/profile/user-6.jpg';
import user7 from 'src/assets/images/profile/user-7.jpg';
import user8 from 'src/assets/images/profile/user-8.jpg';

const performers = [
  {
    id: '1',
    imgsrc: user1,
    name: 'Sunil Joshi',
    rating: 4,
    reviews: 'I like this design',
    date: '1 day ago',
  },
  {
    id: '2',
    imgsrc: user2,
    name: 'Mark Richard',
    rating: 5,
    reviews: 'Awesome quality with great materials used, but could be more comfortable',
    date: '11:20 PM',
  },
  {
    id: '3',
    imgsrc: user3,
    name: 'Hanry Lord',
    rating: 2,
    reviews: 'This is the best product I have ever used.',
    date: 'Today',
  },
  {
    id: '4',
    imgsrc: user4,
    name: 'Britny Cox',
    rating: 3,
    reviews: 'Beautifully crafted. Worth every penny.',
    date: 'Today',
  },
  {
    id: '5',
    imgsrc: user5,
    name: 'Olvin wild',
    rating: 4,
    reviews: 'Beautifully crafted. Worth every penny.',
    date: 'Yesterday',
  },
  {
    id: '6',
    imgsrc: user6,
    name: 'Dan wilsed',
    rating: 4.5,
    reviews: 'Beautifully crafted. Worth every penny.',
    date: '12:00 PM',
  },
  {
    id: '7',
    imgsrc: user7,
    name: 'Jon Miller',
    rating: 4,
    reviews: 'Beautifully crafted. Worth every penny.',
    date: '1 May 2025',
  },
  {
    id: '8',
    imgsrc: user8,
    name: 'Anaa Crown',
    rating: 4,
    reviews: 'Beautifully crafted. Worth every penny.',
    date: '25 April 2025',
  },
];

const CustomersReviews = () => {
  return (
    <Box p={3}>
      <Typography variant="h5" mb={3}>
        Customer Reviews
      </Typography>

      <TableContainer>
        <Table aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell sx={{ pl: 0 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Customer
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="subtitle2" fontWeight={600}>
                  Comment
                </Typography>
              </TableCell>
              <TableCell>
                <Typography textAlign="right" variant="subtitle2" fontWeight={600}>
                  Date
                </Typography>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {performers.map((basic) => (
              <TableRow key={basic.id}>
                <TableCell sx={{ pl: 0 }}>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Avatar src={basic.imgsrc} alt={basic.imgsrc} sx={{ width: 35, height: 35 }} />

                    <Typography variant="subtitle2" fontWeight={600}>
                      {basic.name}
                    </Typography>
                  </Stack>
                </TableCell>
                <TableCell>
                  <Rating name="simple-controlled" value={basic.rating} size="small" />
                  <Typography
                    color="textSecondary"
                    variant="subtitle2"
                    fontSize="14px"
                    fontWeight={400}
                    sx={{
                      maxWidth: { lg: '350px', xs: '150px' },
                      whiteSpace: 'wrap',
                    }}
                  >
                    {basic.reviews}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" textAlign="right">
                    {basic.date}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default CustomersReviews;
