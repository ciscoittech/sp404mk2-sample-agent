// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import {
  Typography,
  Box,
  Avatar,
  LinearProgress,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack
} from '@mui/material';

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';

import img1 from 'src/assets/images/products/s1.jpg';
import img2 from 'src/assets/images/products/s2.jpg';
import img3 from 'src/assets/images/products/s3.jpg';
import img4 from 'src/assets/images/products/s4.jpg';
import ParentCard from 'src/components/shared/ParentCard';
import BlankCard from 'src/components/shared/BlankCard';
import { IconTrash } from '@tabler/icons-react';


interface columnType {
  id: string;
  label: string;
  minWidth: number;
}

interface rowType {
  id: number;
  imgsrc: string;
  name: string;
  tags: string;
  review: string;
  percent: number;
  earnings: string;
}

const columns: columnType[] = [
  { id: 'pname', label: 'Products', minWidth: 170 },
  { id: 'review', label: 'Review', minWidth: 100 },
  {
    id: 'earnings',
    label: 'Earnings',
    minWidth: 170,
  },
  {
    id: 'action',
    label: 'Action',
    minWidth: 170,
  },
];

const rows: rowType[] = [
  {
    id: 1,
    imgsrc: img1,
    name: 'Is it good butterscotch ice-cream?',
    tags: 'Ice-Cream, Milk, Powder',
    review: 'good',
    percent: 65,
    earnings: '546,000',
  },
  {
    id: 2,
    imgsrc: img2,
    name: 'Supreme fresh tomato available',
    tags: 'Market, Mall',
    review: 'excellent',
    percent: 98,
    earnings: '780,000',
  },
  {
    id: 3,
    imgsrc: img3,
    name: 'Red color candy from Gucci',
    tags: 'Chocolate, Yummy',
    review: 'average',
    percent: 46,
    earnings: '457,000',
  },
  {
    id: 4,
    imgsrc: img4,
    name: 'Stylish night lamp for night',
    tags: 'Elecric, Wire, Current',
    review: 'poor',
    percent: 23,
    earnings: '125,000',
  },
];

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Fixed Header Table',
  },
];

const FixedHeaderTable = () => {
  const Capitalize = (str:any) => str.charAt(0).toUpperCase() + str.slice(1);

  return (
    <PageContainer title="Fixed Header Table" description="this is Fixed Header Table page">
      {/* breadcrumb */}
      <Breadcrumb title="Fixed Header Table" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Fixed Header Table">
        <BlankCard>
          <TableContainer
            sx={{
              maxHeight: 440,
            }}
          >
            <Table stickyHeader aria-label="sticky table">
              <TableHead>
                <TableRow>
                  {columns.map((column) => (
                    <TableCell
                      key={column.id}
                      style={{ minWidth: column.minWidth }}
                    >
                      <Typography variant="h6" fontWeight="500">
                        {column.label}
                      </Typography>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => {
                  return (
                    <TableRow hover key={row.id}>
                      <TableCell>
                        <Stack spacing={2} direction="row" alignItems="center">
                          <Avatar
                            src={row.imgsrc}
                            alt={row.imgsrc}
                            sx={{
                              borderRadius: '10px',
                              height: '70px',
                              width: '90px',
                            }}
                          />
                          <Box>
                            <Typography variant="h6">{row.name}</Typography>
                            <Typography color="textSecondary" variant="h6" mt={1} fontWeight="400">
                              {row.tags}
                            </Typography>
                          </Box>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Stack spacing={1}>
                          <Typography
                            variant="subtitle2" fontWeight="500">
                            {Capitalize(row.review)}
                          </Typography>
                          <LinearProgress
                            value={row.percent}
                            variant="determinate" color={row.review === 'good' ? 'primary' : row.review === 'excellent' ? 'success' : row.review === 'average' ? 'warning' : row.review === 'poor' ? 'error' : 'secondary'}
                          />
                          <Typography
                            color="textSecondary"
                            variant="subtitle2"
                            fontWeight="400" whiteSpace="nowrap">
                            {row.percent}% sold
                          </Typography>
                        </Stack>

                      </TableCell>
                      <TableCell>
                        <Stack spacing={1}>
                          <Typography color="textSecondary" variant="subtitle2">
                            Earnings
                          </Typography>
                          <Typography variant="h6">${row.earnings}</Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <IconButton>
                          <IconTrash width={18} />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </BlankCard>

      </ParentCard>
    </PageContainer>
  );
};

export default FixedHeaderTable;
