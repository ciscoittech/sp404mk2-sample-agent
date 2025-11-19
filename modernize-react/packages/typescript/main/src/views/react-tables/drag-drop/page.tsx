import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import Rowdragdrop from 'src/components/react-tables/drag-drop/Rowdragdrop';
import Columndragdrop from 'src/components/react-tables/drag-drop/Columndragdrop'
import { Grid } from '@mui/material';


const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Drag & Drop Table ",
    },
];

function page() {
    return (<>
        <PageContainer title="React Drag & Drop Table" description="this is React  Drag & Drop Table page">
            <Breadcrumb title="Drag & Drop Table " items={BCrumb} />
            <Grid container spacing={3}>
                <Grid sx={{ padding: 2 }} size={12}>
                    <Rowdragdrop />
                </Grid>
                <Grid sx={{ padding: 2 }} size={12}>
                    <Columndragdrop />
                </Grid>
            </Grid>
        </PageContainer>
    </>);
}

export default page;
