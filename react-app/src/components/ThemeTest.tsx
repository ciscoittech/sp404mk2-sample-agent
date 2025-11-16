import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"

export default function ThemeTest() {
  return (
    <div className="dark min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">
            ShadCN UI Theme Test
          </h1>
          <p className="text-muted-foreground">
            Professional music production dark theme with cyan and green accents
          </p>
        </div>

        <Separator />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Sample Analysis</CardTitle>
              <CardDescription>Audio processing controls</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="sample-name">Sample Name</Label>
                <Input id="sample-name" placeholder="Enter sample name..." />
              </div>

              <div className="space-y-2">
                <Label>BPM: 120</Label>
                <Slider defaultValue={[120]} max={200} min={60} step={1} />
              </div>

              <div className="flex gap-2">
                <Button variant="default">Analyze</Button>
                <Button variant="secondary">Cancel</Button>
                <Button variant="outline">Reset</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Processing Status</CardTitle>
              <CardDescription>Current analysis progress</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="text-foreground">75%</span>
                </div>
                <Progress value={75} />
              </div>

              <div className="flex flex-wrap gap-2">
                <Badge variant="default">Analyzing</Badge>
                <Badge variant="secondary">120 BPM</Badge>
                <Badge variant="outline">Hip-Hop</Badge>
              </div>

              <div className="space-y-2">
                <Button className="w-full" variant="default">
                  Primary Action
                </Button>
                <Button className="w-full bg-accent text-accent-foreground hover:bg-accent/90">
                  Success Action
                </Button>
                <Button className="w-full" variant="destructive">
                  Delete Sample
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Color Palette Preview</CardTitle>
            <CardDescription>
              Professional music production theme - NO purple gradients
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-background border-2 border-border" />
                <p className="text-xs text-muted-foreground">Background</p>
              </div>
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-primary" />
                <p className="text-xs text-muted-foreground">Primary (Cyan)</p>
              </div>
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-accent" />
                <p className="text-xs text-muted-foreground">Accent (Green)</p>
              </div>
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-destructive" />
                <p className="text-xs text-muted-foreground">Destructive (Red)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
