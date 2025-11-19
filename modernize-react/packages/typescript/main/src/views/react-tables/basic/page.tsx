import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ReactBasicTables from 'src/components/react-tables/basic/page';


const BCrumb = [
    {
        to: '/',
        title: 'Home',
    },
    {
        title: ' React Basic Table',
    },
];


function page() {
    return (
        <>
            <PageContainer title="React Basic Table" description="this is React  Basic Table page">
                <Breadcrumb title="React Basic Table" items={BCrumb} />
                <div>
                    <ReactBasicTables />
                </div>
            </PageContainer>
        </>
    )
}

export default page
