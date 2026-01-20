using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System.Collections.Generic;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CSampleChunkNode
    {
        public char* name;
        public int value;
        public bool isDataNode;
        public CSampleChunkNode* child;
        public CSampleChunkNode* sibling;

        public static CSampleChunkNode* FromSampleChunkNodeTree(SampleChunkNode? root)
        {
            if (root == null)
            {
                return null;
            }

            List<SampleChunkNode> flatNodes = [];
            AddNodes(flatNodes, root);

            CSampleChunkNode* result = Allocate.Alloc<CSampleChunkNode>(flatNodes.Count);

            for (int i = 0; i < flatNodes.Count; i++)
            {
                CSampleChunkNode* resultNode = &result[i];
                SampleChunkNode node = flatNodes[i];

                resultNode->name = node.Name.AllocString();
                resultNode->value = node.SignedValue;
                resultNode->isDataNode = node.Data != null;
                resultNode->child = node.Children.Count > 0 ? &result[flatNodes.IndexOf(node.Children[0])] : null;

                SampleChunkNode? sibling = null;
                if (node.Parent != null)
                {
                    int parentIndex = node.Parent.Children.IndexOf(node);
                    if (parentIndex < node.Parent.Children.Count - 1)
                    {
                        sibling = node.Parent.Children[parentIndex + 1];
                    }
                }

                resultNode->sibling = sibling != null ? &result[flatNodes.IndexOf(sibling)] : null;
            }

            return result;
        }

        private static void AddNodes(List<SampleChunkNode> destination, SampleChunkNode node)
        {
            destination.Add(node);
            foreach (SampleChunkNode child in node)
            {
                AddNodes(destination, child);
            }
        }

        public readonly SampleChunkNode ToSampleChunkNodeTree(SampleChunkResource? target)
        {
            SampleChunkNode result = new(Util.ToString(name)!, value);

            if (isDataNode)
            {
                result.Data = target;
            }

            if (child != null)
            {
                CSampleChunkNode* currentChild = child;
                while (currentChild != null)
                {
                    result.AddChild(currentChild->ToSampleChunkNodeTree(target));
                    currentChild = currentChild->sibling;
                }
            }

            return result;
        }

    }
}
